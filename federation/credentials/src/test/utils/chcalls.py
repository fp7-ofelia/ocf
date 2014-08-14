import credparsing as credutils
import os.path
import re
import xmlrpclib
from settings.src.settings import MY_ROOTS_DIR


def api_call(method_name, endpoint, params=[], user_name='alice', verbose=False):
    key_path, cert_path = "%s-key.pem" % (user_name,), "%s-cert.pem" % (user_name,)
    res = ssl_call(method_name, params, endpoint, key_path=key_path, cert_path=cert_path)
    if verbose:
        print method_name, params, res
    return res.get('code', None), res.get('value', None), res.get('output', None)

def ch_call(method_name, endpoint="", params=[], user_name='alice', verbose=False):
    key_path, cert_path = "%s-key.pem" % (user_name,), "%s-cert.pem" % (user_name,)
    res = ssl_call(method_name, params, endpoint, key_path=key_path, cert_path=cert_path, host='127.0.0.1', port=8000)
    return res

class SafeTransportWithCert(xmlrpclib.SafeTransport):
    """Helper class to force the right certificate for the transport class."""
    def __init__(self, key_path, cert_path):
        xmlrpclib.SafeTransport.__init__(self) # no super, because old style class
        self._key_path = key_path
        self._cert_path = cert_path

    def make_connection(self, host):
        """This method will automatically be called by the ServerProxy class when a transport channel is needed."""
        host_with_cert = (host, {'key_file' : self._key_path, 'cert_file' : self._cert_path})
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) # no super, because old style class

def ssl_call(method_name, params, endpoint, key_path='alice-key.pem', cert_path='alice-cert.pem', host='127.0.0.1', port=8440):
    #creds_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'cert'))
    creds_path = MY_ROOTS_DIR
    if not os.path.isabs(key_path):
        key_path = os.path.join(creds_path, key_path)
    if not os.path.isabs(cert_path):
        cert_path = os.path.join(creds_path, cert_path)
    key_path = os.path.abspath(os.path.expanduser(key_path))
    cert_path = os.path.abspath(os.path.expanduser(cert_path))
    if not os.path.isfile(key_path) or not os.path.isfile(cert_path):
        raise RuntimeError("Key or cert file not found (%s, %s)" % (key_path, cert_path))
    transport = SafeTransportWithCert(key_path, cert_path)
    proxy = xmlrpclib.ServerProxy("https://%s:%s/%s" % (host, str(port), endpoint), transport=transport)
    # return proxy.get_version()
    method = getattr(proxy, method_name)
    return method(*params)

def wrap_cred(cred):
    """
    Wrap the given cred in the appropriate struct for this framework.
    """
    if isinstance(cred, dict):
        print "Called wrap on a cred that's already a dict? %s", cred
        return cred
    elif not isinstance(cred, str):
        print "Called wrap on non string cred? Stringify. %s", cred
        cred = str(cred)
    ret = dict(geni_type="geni_sfa", geni_version="2", geni_value=cred)
    if credutils.is_valid_v3(None, cred):
        ret["geni_version"] = "3"
    return ret

def getusercred(user_cert_filename = "alice-cert.pem", geni_api = 3):
    """Retrieve your user credential. Useful for debugging.

    If you specify the -o option, the credential is saved to a file.
    If you specify --usercredfile:
       First, it tries to read the user cred from that file.
       Second, it saves the user cred to a file by that name (but with the appropriate extension)
    Otherwise, the filename is <username>-<framework nickname from config file>-usercred.[xml or json, depending on AM API version].
    If you specify the --prefix option then that string starts the filename.

    If instead of the -o option, you supply the --tostdout option, then the usercred is printed to STDOUT.
    Otherwise the usercred is logged.

    The usercred is returned for use by calling scripts.

    e.g.:
      Get user credential, save to a file:
        omni.py -o getusercred

      Get user credential, save to a file with filename prefix mystuff:
        omni.py -o -p mystuff getusercred
"""
    #creds_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'cert'))
    creds_path = MY_ROOTS_DIR
    cert_path = os.path.join(creds_path, user_cert_filename)
    user_cert = open(cert_path, "r").read()
    # Contacting GCH for it by passing the certificate
    cred = ch_call("CreateUserCredential", params = [user_cert])
    #(cred, message) = ch_call(method_name = "CreateUserCredential", endpoint = "", params = {"params": user_cert})
    if geni_api >= 3:
        if cred:
            cred = wrap_cred(cred)
    credxml = credutils.get_cred_xml(cred)
    # pull the username out of the cred
    # <owner_urn>urn:publicid:IDN+geni:gpo:gcf+user+alice</owner_urn>
    user = ""
    usermatch = re.search(r"\<owner_urn>urn:publicid:IDN\+.+\+user\+(\w+)\<\/owner_urn\>", credxml)
    if usermatch:
        user = usermatch.group(1)
    return "Retrieved %s user credential" % user, cred

def get_creds_file_contents(filename):
    #creds_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'creds'))
    creds_path = MY_ROOTS_DIR
    if not os.path.isabs(filename):
        filename = os.path.join(creds_path, filename)
    filename = os.path.abspath(os.path.expanduser(filename))
    contents = None
    with open(filename, 'r') as f:
        contents = f.read()
    return contents