#----------------------------------------------------------------------
# Copyright (c) 2014 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

from __future__ import absolute_import

import datetime
from dateutil import parser as du_parser, tz as du_tz
import optparse
import os
import subprocess
import sys
import tempfile
from xml.dom.minidom import *
from StringIO import StringIO

from credentials.src.trustgcf.abac_credential import ABACCredential, ABACElement
from credentials.src.trustgcf.certificate import Certificate
from credentials.src.trustgcf.credential import Credential, signature_template, HAVELXML
from credentials.src.trustgcf.credential_factory import CredentialFactory
from credentials.src.trustgcf.gid import GID


# Routine to validate that a speaks-for credential 
# says what it claims to say:
# It is a signed credential wherein the signer S is attesting to the
# ABAC statement:
# S.speaks_for(S)<-T Or "S says that T speaks for S"

# Requires that openssl be installed and in the path
# create_speaks_for requires that xmlsec1 be on the path

# Simple XML helper functions

# Find the text associated with first child text node
def findTextChildValue(root):
    child = findChildNamed(root, '#text')
    if child: return str(child.nodeValue)
    return None

# Find first child with given name
def findChildNamed(root, name):
    for child in root.childNodes:
        if child.nodeName == name:
            return child
    return None

# Write a string to a tempfile, returning name of tempfile
def write_to_tempfile(str):
    str_fd, str_file = tempfile.mkstemp()
    if str:
        os.write(str_fd, str)
    os.close(str_fd)
    return str_file

# Run a subprocess and return output
def run_subprocess(cmd, stdout, stderr):
    try:
        proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
        proc.wait()
        if stdout:
            output = proc.stdout.read()
        else:
            output = proc.returncode
        return output
    except Exception as e:
        raise Exception("Failed call to subprocess '%s': %s" % (" ".join(cmd), e))

def get_cert_keyid(gid):
    """Extract the subject key identifier from the given certificate.
    Return they key id as lowercase string with no colon separators
    between pairs. The key id as shown in the text output of a
    certificate are in uppercase with colon separators.

    """
    raw_key_id = gid.get_extension('subjectKeyIdentifier')
    # Raw has colons separating pairs, and all characters are upper case.
    # Remove the colons and convert to lower case.
    keyid = raw_key_id.replace(':', '').lower()
    return keyid

# Pull the cert out of a list of certs in a PEM formatted cert string
def grab_toplevel_cert(cert):
    start_label = '-----BEGIN CERTIFICATE-----'
    if cert.find(start_label) > -1:
        start_index = cert.find(start_label) + len(start_label)
    else:
        start_index = 0
    end_label = '-----END CERTIFICATE-----'
    end_index = cert.find(end_label)
    first_cert = cert[start_index:end_index]
    pieces = first_cert.split('\n')
    first_cert = "".join(pieces)
    return first_cert

# Validate that the given speaks-for credential represents the
# statement User.speaks_for(User)<-Tool for the given user and tool certs
# and was signed by the user
# Return: 
#   Boolean indicating whether the given credential 
#      is not expired 
#      is an ABAC credential
#      was signed by the user associated with the speaking_for_urn
#      is verified by xmlsec1
#      asserts U.speaks_for(U)<-T ("user says that T may speak for user")
#      If schema provided, validate against schema
#      is trusted by given set of trusted roots (both user cert and tool cert)
#   String user certificate of speaking_for user if the above tests succeed
#      (None otherwise)
#   Error message indicating why the speaks_for call failed ("" otherwise)
def verify_speaks_for(cred, tool_gid, speaking_for_urn, \
                          trusted_roots, schema=None, logger=None):

    # Credential has not expired
    if cred.expiration and cred.expiration < datetime.datetime.utcnow():
        return False, None, "ABAC Credential expired at %s (%s)" % (cred.expiration.isoformat(), cred.get_summary_tostring())

    # Must be ABAC
    if cred.get_cred_type() != ABACCredential.ABAC_CREDENTIAL_TYPE:
        return False, None, "Credential not of type ABAC but %s" % cred.get_cred_type

    if cred.signature is None or cred.signature.gid is None:
        return False, None, "Credential malformed: missing signature or signer cert. Cred: %s" % cred.get_summary_tostring()
    user_gid = cred.signature.gid
    user_urn = user_gid.get_urn()

    # URN of signer from cert must match URN of 'speaking-for' argument
    if user_urn != speaking_for_urn:
        return False, None, "User URN from cred doesn't match speaking_for URN: %s != %s (cred %s)" % \
            (user_urn, speaking_for_urn, cred.get_summary_tostring())

    tails = cred.get_tails()
    if len(tails) != 1: 
        return False, None, "Invalid ABAC-SF credential: Need exactly 1 tail element, got %d (%s)" % \
            (len(tails), cred.get_summary_tostring())

    user_keyid = get_cert_keyid(user_gid)
    tool_keyid = get_cert_keyid(tool_gid)
    subject_keyid = tails[0].get_principal_keyid()

    head = cred.get_head()
    principal_keyid = head.get_principal_keyid()
    role = head.get_role()

    # Credential must pass xmlsec1 verify
    cred_file = write_to_tempfile(cred.save_to_string())
    cert_args = []
    if trusted_roots:
        for x in trusted_roots:
            cert_args += ['--trusted-pem', x.filename]
    # FIXME: Why do we not need to specify the --node-id option as credential.py does?
    xmlsec1_args = [cred.xmlsec_path, '--verify'] + cert_args + [ cred_file]
    output = run_subprocess(xmlsec1_args, stdout=None, stderr=subprocess.PIPE)
    os.unlink(cred_file)
    if output != 0:
        # FIXME
        # xmlsec errors have a msg= which is the interesting bit.
        # But does this go to stderr or stdout? Do we have it here?
        verified = ""
        mstart = verified.find("msg=")
        msg = ""
        if mstart > -1 and len(verified) > 4:
            mstart = mstart + 4
            mend = verified.find('\\', mstart)
            msg = verified[mstart:mend]
        if msg == "":
            msg = output
        return False, None, "ABAC credential failed to xmlsec1 verify: %s" % msg

    # Must say U.speaks_for(U)<-T
    if user_keyid != principal_keyid or \
            tool_keyid != subject_keyid or \
            role != ('speaks_for_%s' % user_keyid):
        return False, None, "ABAC statement doesn't assert U.speaks_for(U)<-T (%s)" % cred.get_summary_tostring()

    # If schema provided, validate against schema
    if HAVELXML and schema and os.path.exists(schema):
        from lxml import etree
        tree = etree.parse(StringIO(cred.xml))
        schema_doc = etree.parse(schema)
        xmlschema = etree.XMLSchema(schema_doc)
        if not xmlschema.validate(tree):
            error = xmlschema.error_log.last_error
            message = "%s: %s (line %s)" % (cred.get_summary_tostring(), error.message, error.line)
            return False, None, ("XML Credential schema invalid: %s" % message)

    if trusted_roots:
        # User certificate must validate against trusted roots
        try:
            user_gid.verify_chain(trusted_roots)
        except Exception, e:
            return False, None, \
                "Cred signer (user) cert not trusted: %s" % e

        # Tool certificate must validate against trusted roots
        try:
            tool_gid.verify_chain(trusted_roots)
        except Exception, e:
            return False, None, \
                "Tool cert not trusted: %s" % e

    return True, user_gid, ""

# Determine if this is a speaks-for context. If so, validate
# And return either the tool_cert (not speaks-for or not validated)
# or the user cert (validated speaks-for)
#
# credentials is a list of GENI-style credentials:
#  Either a cred string xml string, or Credential object of a tuple
#    [{'geni_type' : geni_type, 'geni_value : cred_value, 
#      'geni_version' : version}]
# caller_gid is the raw X509 cert gid
# options is the dictionary of API-provided options
# trusted_roots is a list of Certificate objects from the system
#   trusted_root directory
# Optionally, provide an XML schema against which to validate the credential
def determine_speaks_for(logger, credentials, caller_gid, options, \
                             trusted_roots, schema=None):
    if options and 'geni_speaking_for' in options:
        speaking_for_urn = options['geni_speaking_for'].strip()
        for cred in credentials:
            # Skip things that aren't ABAC credentials
            if type(cred) == dict:
                if cred['geni_type'] != ABACCredential.ABAC_CREDENTIAL_TYPE: continue
                cred_value = cred['geni_value']
            elif isinstance(cred, Credential):
                if not isinstance(cred, ABACCredential):
                    continue
                else:
                    cred_value = cred
            else:
                if CredentialFactory.getType(cred) != ABACCredential.ABAC_CREDENTIAL_TYPE: continue
                cred_value = cred

            # If the cred_value is xml, create the object
            if not isinstance(cred_value, ABACCredential):
                cred = CredentialFactory.createCred(cred_value)

#            print "Got a cred to check speaksfor for: %s" % cred.get_summary_tostring()
#            #cred.dump(True, True)
#            print "Caller: %s" % caller_gid.dump_string(2, True)

            # See if this is a valid speaks_for
            is_valid_speaks_for, user_gid, msg = \
                verify_speaks_for(cred,
                                  caller_gid, speaking_for_urn, \
                                      trusted_roots, schema, logger)

            if is_valid_speaks_for:
                return user_gid # speaks-for
            else:
                if logger:
                    logger.info("Got speaks-for option but not a valid speaks_for with this credential: %s" % msg)
                else:
                    print "Got a speaks-for option but not a valid speaks_for with this credential: " + msg
    return caller_gid # Not speaks-for

# Create an ABAC Speaks For credential using the ABACCredential object and it's encode&sign methods
def create_sign_abaccred(tool_gid, user_gid, ma_gid, user_key_file, cred_filename, dur_days=365):
    print "Creating ABAC SpeaksFor using ABACCredential...\n"
    # Write out the user cert
    from tempfile import mkstemp
    ma_str = ma_gid.save_to_string()
    user_cert_str = user_gid.save_to_string()
    if not user_cert_str.endswith(ma_str):
        user_cert_str += ma_str
    fp, user_cert_filename = mkstemp(suffix='cred', text=True)
    fp = os.fdopen(fp, "w")
    fp.write(user_cert_str)
    fp.close()

    # Create the cred
    cred = ABACCredential()
    cred.set_issuer_keys(user_key_file, user_cert_filename)
    tool_urn = tool_gid.get_urn()
    user_urn = user_gid.get_urn()
    user_keyid = get_cert_keyid(user_gid)
    tool_keyid = get_cert_keyid(tool_gid)
    cred.head = ABACElement(user_keyid, user_urn, "speaks_for_%s" % user_keyid)
    cred.tails.append(ABACElement(tool_keyid, tool_urn))
    cred.set_expiration(datetime.datetime.utcnow() + datetime.timedelta(days=dur_days))
    cred.expiration = cred.expiration.replace(microsecond=0)

    # Produce the cred XML
    cred.encode()

    # Sign it
    cred.sign()
    # Save it
    cred.save_to_file(cred_filename)
    print "Created ABAC credential: '%s' in file %s" % \
            (cred.get_summary_tostring(), cred_filename)

# FIXME: Assumes xmlsec1 is on path
# FIXME: Assumes signer is itself signed by an 'ma_gid' that can be trusted
def create_speaks_for(tool_gid, user_gid, ma_gid, \
                          user_key_file, cred_filename, dur_days=365):
    tool_urn = tool_gid.get_urn()
    user_urn = user_gid.get_urn()

    header = '<?xml version="1.0" encoding="UTF-8"?>'
    reference = "ref0"
    signature_block = \
        '<signatures>\n' + \
        signature_template + \
        '</signatures>'
    template = header + '\n' + \
        '<signed-credential '
    template += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.geni.net/resources/credential/2/credential.xsd" xsi:schemaLocation="http://www.protogeni.net/resources/credential/ext/policy/1 http://www.protogeni.net/resources/credential/ext/policy/1/policy.xsd"'
    template += '>\n' + \
        '<credential xml:id="%s">\n' + \
        '<type>abac</type>\n' + \
        '<serial/>\n' +\
        '<owner_gid/>\n' + \
        '<owner_urn/>\n' + \
        '<target_gid/>\n' + \
        '<target_urn/>\n' + \
        '<uuid/>\n' + \
        '<expires>%s</expires>' +\
        '<abac>\n' + \
        '<rt0>\n' + \
        '<version>%s</version>\n' + \
        '<head>\n' + \
        '<ABACprincipal><keyid>%s</keyid><mnemonic>%s</mnemonic></ABACprincipal>\n' +\
        '<role>speaks_for_%s</role>\n' + \
        '</head>\n' + \
        '<tail>\n' +\
        '<ABACprincipal><keyid>%s</keyid><mnemonic>%s</mnemonic></ABACprincipal>\n' +\
        '</tail>\n' +\
        '</rt0>\n' + \
        '</abac>\n' + \
        '</credential>\n' + \
        signature_block + \
        '</signed-credential>\n'


    credential_duration = datetime.timedelta(days=dur_days)
    expiration = datetime.datetime.now(du_tz.tzutc()) + credential_duration
    expiration_str = expiration.strftime('%Y-%m-%dT%H:%M:%SZ') # FIXME: libabac can't handle .isoformat()
    version = "1.1"

    user_keyid = get_cert_keyid(user_gid)
    tool_keyid = get_cert_keyid(tool_gid)
    unsigned_cred = template % (reference, expiration_str, version, \
                                    user_keyid, user_urn, user_keyid, tool_keyid, tool_urn, \
                                    reference, reference)
    unsigned_cred_filename = write_to_tempfile(unsigned_cred)

    # Now sign the file with xmlsec1
    # xmlsec1 --sign --privkey-pem privkey.pem,cert.pem 
    # --output signed.xml tosign.xml
    pems = "%s,%s,%s" % (user_key_file, user_gid.get_filename(),
                         ma_gid.get_filename())
    # FIXME: assumes xmlsec1 is on path
    cmd = ['xmlsec1',  '--sign',  '--privkey-pem', pems, 
           '--output', cred_filename, unsigned_cred_filename]

#    print " ".join(cmd)
    sign_proc_output = run_subprocess(cmd, stdout=subprocess.PIPE, stderr=None)
    if sign_proc_output == None:
        print "OUTPUT = %s" % sign_proc_output
    else:
        print "Created ABAC credential: '%s speaks_for %s' in file %s" % \
            (tool_urn, user_urn, cred_filename)
    os.unlink(unsigned_cred_filename)


# Test procedure
if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option('--cred_file', 
                      help='Name of credential file')
    parser.add_option('--tool_cert_file', 
                      help='Name of file containing tool certificate')
    parser.add_option('--user_urn', 
                      help='URN of speaks-for user')
    parser.add_option('--user_cert_file', 
                      help="filename of x509 certificate of signing user")
    parser.add_option('--ma_cert_file', 
                      help="filename of x509 cert of MA that signed user cert")
    parser.add_option('--user_key_file', 
                      help="filename of private key of signing user")
    parser.add_option('--trusted_roots_directory', 
                      help='Directory of trusted root certs')
    parser.add_option('--create',
                      help="name of file of ABAC speaksfor cred to create")
    parser.add_option('--useObject', action='store_true', default=False,
                      help='Use the ABACCredential object to create the credential (default False)')

    options, args = parser.parse_args(sys.argv)

    tool_gid = GID(filename=options.tool_cert_file)

    if options.create:
        if options.user_cert_file and options.user_key_file \
            and options.ma_cert_file:
            user_gid = GID(filename=options.user_cert_file)
            ma_gid = GID(filename=options.ma_cert_file)
            if options.useObject:
                create_sign_abaccred(tool_gid, user_gid, ma_gid, \
                                         options.user_key_file,  \
                                         options.create)
            else:
                create_speaks_for(tool_gid, user_gid, ma_gid, \
                                         options.user_key_file,  \
                                         options.create)
        else:
            print "Usage: --create cred_file " + \
                "--user_cert_file user_cert_file" + \
                " --user_key_file user_key_file --ma_cert_file ma_cert_file"
        sys.exit()

    user_urn = options.user_urn

    # Get list of trusted rootcerts
    if options.cred_file and not options.trusted_roots_directory:
        sys.exit("Must supply --trusted_roots_directory to validate a credential")

    trusted_roots_directory = options.trusted_roots_directory
    trusted_roots = \
        [Certificate(filename=os.path.join(trusted_roots_directory, file)) \
             for file in os.listdir(trusted_roots_directory) \
             if file.endswith('.pem') and file != 'CATedCACerts.pem']

    cred = open(options.cred_file).read()

    creds = [{'geni_type' : ABACCredential.ABAC_CREDENTIAL_TYPE, 'geni_value' : cred, 
              'geni_version' : '1'}]
    gid = determine_speaks_for(None, creds, tool_gid, \
                                   {'geni_speaking_for' : user_urn}, \
                                   trusted_roots)


    print 'SPEAKS_FOR = %s' % (gid != tool_gid)
    print "CERT URN = %s" % gid.get_urn()
