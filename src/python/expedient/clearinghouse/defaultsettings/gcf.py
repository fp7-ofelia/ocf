'''Settings for interacting with GENI Control Framework aggregates.

Created on Aug 19, 2010

@author: jnaous
'''
from os.path import join
from django import CONF_DIR

GCF_BASE_NAME = "stanford//expedient"
'''The domain name used in URNs when creating certificates mainly.

You will need to override this for your deployment to change "stanford"
to your site's name.

This must not have any spaces or illegal characters not allowed in
URNs or you will get cryptic errors.

This should look something like "stanford//expedient"

'''

GCF_URN_AM_SUFFIX = "authority+am"
'''The suffix of the GCF AM URN.

This gets appended to the URN prefix obtained from the L{GCF_BASE_NAME}.
Default (and required by convention) is "authority+am".

'''

# Location of GENI x509 certs and keys
GCF_X509_CERT_DIR = join(CONF_DIR, "gcf-x509.crt")
'''The location of certificates used by expedient for the GCF.'''

GCF_X509_KEY_DIR = join(CONF_DIR, "gcf-x509.key")
'''The location of keys used by expedient for the GCF.'''

GCF_X509_CRED_DIR = join(CONF_DIR, "gcf-x509.cred")
'''The location of credentials used by expedient for the GCF.'''

GCF_X509_CH_CERT = join(GCF_X509_CERT_DIR, "ch.crt")
'''The absolute path of the Clearinghouse certificate for Expedient.'''

GCF_X509_CH_KEY = join(GCF_X509_KEY_DIR, "ch.key")
'''The absolute path of the Clearinghouse key for Expedient.'''

GCF_NULL_SLICE_CRED = join(GCF_X509_CRED_DIR, "ch.cred")
'''The default slice's full credentials.'''

CURRENT_GAPI_VERSION = 1
'''The latest version of the GENI API'''

GCF_X509_USER_CERT_FNAME_PREFIX = "user_x509_"
'''The prefix to prepend to the filenames of saved user certificates.'''

GCF_MAX_UPLOADED_PEM_FILE_SIZE = 1024*1024
'''Maximum size of uploaded certificate or key files in bytes.'''
