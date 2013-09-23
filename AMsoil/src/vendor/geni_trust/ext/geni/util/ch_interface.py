#----------------------------------------------------------------------
# Copyright (c) 2012-2013 Raytheon BBN Technologies
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

# Library of tools for communicating with the GENI clearinghouse
# services via XML signed encrypted messages.
# Receiving back a tuple with [code, value, output]
# if code = 0, value is the result
# if code is not 0, the output is additional info on the error

import json
import os
import tempfile
import traceback
import urllib2
import M2Crypto

# TODO: 
# - Change get_inside_cert_and_key to use GID.py to get URN and UUID from cert
# --- caller needs to pass in _server.pem_cert
#        user_certstr = addMACert(self._server.pem_cert, self.logger, self.macert)
#
#        try:
#            user_gid = gid.GID(string=user_certstr)
#        except Exception, exc:
#            self.logger.error("GetCredential failed to create user_gid from SSL client cert: %s", traceback.format_exc())
#            raise Exception("Failed to GetCredential. Cant get user GID from SSL client certificate." % exc)
#
#        try:
#            user_gid.verify_chain(self.trusted_roots)
#        except Exception, exc:
#            self.logger.error("GetCredential got unverifiable experimenter cert: %s", exc)
#            raise

# Then getting a UUID or URN is something like this:
#        user_uuid = str(uuid.UUID(int=user_gid.get_uuid()))
#        user_urn = user_gid.get_urn()

# FIXME: The CH APIs have, I believe, evolved since this was written. Must update!

# Helper function to get the insert cert/key for a given connection
# Based on the SSL cert on the given connection
def get_inside_cert_and_key(peercert, ma_url, logger):

#   print(str(peercert))
    san = peercert.get('subjectAltName');
    uri = None
    uuid = None
    for e in san:
        key = e[0];
        value = e[1];
        if(key == 'URI' and "IDN+" in value):
            uri = value;
        if(key == 'URI' and 'uuid' in value):
            uuid_parts = value.split(':');
            uuid = uuid_parts[2];
#           print "URI = " + str(uri) +  " UUID = " + str(uuid)
            args = dict(member_id = uuid)
            row = invokeCH(ma_url, 'lookup_keys_and_certs', logger, args)
        
#    logger.info("ROW = " + str(row))
    result = dict();
    if(row['code'] == 0):
        row_raw = row['value'];
        private_key = row_raw['private_key']
        certificate = row_raw['certificate']
        (key_fid, key_fname) = tempfile.mkstemp()
        os.write(key_fid, private_key);
        os.close(key_fid);
        (cert_fid, cert_fname) = tempfile.mkstemp();
        os.write(cert_fid, certificate);
        os.close(cert_fid);
        result = {'key': key_fname, 'cert':cert_fname};
        
    return result;
            

# Force the unicode strings python creates to be ascii
def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

# Force the unicode strings python creates to be ascii
def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def decodeCHResponse(msg, logger):
    """Decode the response from the Clearinghouse. It might be encrypted,
    and it might be signed, and it's certainly JSON. Figure out what's what
    and return the decoded JSON.

    See http://svn.osafoundation.org/m2crypto/trunk/doc/howto.smime.html
    """
    #--------------------------------------------------
    # FIXME: Add support for encryption.
    # FIXME: Add signature verfication (see FIXME below)
    #--------------------------------------------------
    #logger.debug("Entering decodeCHResponse with msg=%s", msg);
    # Remove whitespace -- it seems to negatively impact SMIME decoding.
    msg = msg.strip()
    # Load the message into an OpenSSL IO buffer
    p7_bio = M2Crypto.BIO.MemoryBuffer(msg)
    # Try to load the msg as a PKCS7 (SMIME) message.
    json_data = None
    try:
        p7, data = M2Crypto.SMIME.smime_load_pkcs7_bio(p7_bio)
        #logger.debug("decodeCHResponse: SMIME loaded");
        # FIXME: Should verify here
        json_data = data.read()
    except M2Crypto.SMIME.SMIME_Error, err:
        logger.error("SMIME_Error: %s", err)
        #logger.debug("decodeCHResponse: Handling SMIME exception");
        json_data = msg
    result = json.loads(json_data, encoding='ascii', object_hook=_decode_dict)
    return result

def sign_message(key, certs, msg):
    """Signs 'msg' and returns the multipart S/MIME signed message.
    More info can be found in the "howto.smime.html" file in the
    M2Crypto source.
    """
    # Create an SMIME signer
    smime = M2Crypto.SMIME.SMIME()
    # Load the key and cert to use for signing
    smime.load_key_bio(M2Crypto.BIO.MemoryBuffer(key),
                       M2Crypto.BIO.MemoryBuffer(certs[0]))
    # Add the cert chain, if there is one
    if len(certs) > 1:
        sk = M2Crypto.X509.X509_Stack()
        for c in certs[1:]:
            # Load up a cert chain
            sk.push(M2Crypto.X509.load_cert_bio(M2Crypto.BIO.MemoryBuffer(c)))
        # Add the chain certs to the smime signer
        smime.set_x509_stack(sk)
    # Load the msg into a BIO
    msg_bio = M2Crypto.BIO.MemoryBuffer(msg)
    # get the signature
    p7 = smime.sign(msg_bio)
    # Create a temporary BIO to hold the multipart message
    tmp_bio = M2Crypto.BIO.MemoryBuffer()
    # Load the msg into a BIO again -- wish I could rewind instead
    msg_bio = M2Crypto.BIO.MemoryBuffer(msg)
    # Write the multipart message to the temporary BIO
    smime.write(tmp_bio, p7, msg_bio)
    # Extract the multipart message from the temporary BIO
    signed_message = tmp_bio.read()
    return signed_message

def invokeCH(url, operation, logger, argsdict, mycerts=None, mykey=None):
    # Invoke the real CH
    # for now, this should json encode the args and operation, do an http put
    # entry 1 in dict is named operation and is the operation, rest are args
    # json decode result, getting a dict
    # return the result
    if not operation or operation.strip() == '':
        raise Exception("missing operation")
    if not url or url.strip() == '':
        raise Exception("missing url")
    if not argsdict:
        raise Exception("missing argsdict")

    # Put operation in front of argsdict
    toencode = dict(operation=operation)
    for (k,v) in argsdict.items():
        toencode[k]=v
    argstr = json.dumps(toencode)
    if (mycerts and mykey):
        argstr = sign_message(mykey, mycerts, argstr)
    logger.debug("Will do put of %s", argstr)
#    print ("Doing  put of %s" % argstr)

    # now http put this, grab result into putres
    # This is the most trivial put client. This appears to be harder to do / less common than you would expect.
    # See httplib2 for an alternative approach using another library.
    # This approach isn't very robust, may have other issues
    opener = urllib2.build_opener(urllib2.HTTPSHandler)
    req = urllib2.Request(url, data=argstr)
    req.add_header('Content-Type', 'application/json')
    req.get_method = lambda: 'PUT'

    putres = None
    putresHandle = None
    try:
        putresHandle = opener.open(req)
    except Exception, e:
        logger.error("invokeCH failed to open conn to %s: %s", url, e)
        raise Exception("invokeCH failed to open conn to %s: %s" % (url, e))

    if putresHandle:
        try:
            putres=putresHandle.read()
        except Exception, e:
            logger.error("invokeCH failed to read result of put to %s: %s", url, e)
            raise Exception("invokeCH failed to read result of put to %s: %s" % (url, e))

    resdict = None
    if putres:
        logger.debug("invokeCH Got result of %s" % putres)
        resdict = decodeCHResponse(putres, logger)
    
    # FIXME: Check for code, value, output keys?
    return resdict

def getValueFromTriple(triple, logger, opname, unwrap=False):
    if not triple:
        logger.error("Got empty result triple after %s" % opname)
        raise Exception("Return struct was null for %s" % opname)
    if not isinstance(triple, dict) or not triple.has_key('value'):
        logger.error("Malformed return from %s: %s" % (opname, triple))
        raise Exception("malformed return from %s: %s" % (opname, triple))
    if unwrap:
        return triple['value']
    else:
        return triple

# Wait for pyOpenSSL v0.13 which will let us get the client cert chain from the SSL connection
# for now, assume all experimenters are issued by the local MA
def addMACert(experimenter_cert, logger, macertpath):
#/usr/share/geni-ch/ma/ma-cert.pem
    if macertpath is None or macertpath.strip() == '':
        return experimenter_cert

    mc = ''
    add = False
    try:
        with open(macertpath) as macert:
            for line in macert:
                if add or ("BEGIN CERT" in line):
                    add = True
                    mc += line
#            mc = macert.read()
    except:
        logger.error("Failed to read MA cert: %s", traceback.format_exc())
    logger.debug("Resulting PEM: %s" % (experimenter_cert + mc))
    return experimenter_cert + mc
