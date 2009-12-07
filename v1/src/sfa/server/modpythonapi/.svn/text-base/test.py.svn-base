import sys
import traceback

from BaseClient import BaseClient, EnableVerboseExceptions
from AuthenticatedClient import AuthenticatedClient

EnableVerboseExceptions(True)

HOST = "localhost"
URL = "http://" + HOST + "/TESTAPI/"
SURL = "https://" + HOST + "/TESTAPI/"

print "*** testing some valid ops; these should print \"Hello, World\" ***"

bc = BaseClient(URL)
print "HTTP noop:", bc.noop("Hello, World")

ac = AuthenticatedClient(URL, "gackstestuser.pkey", "gackstestuser.gid")
print "HTTP gidNoop:", ac.gidNoop("Hello, World")

bc = BaseClient(SURL)
print "HTTPS noop:", bc.noop("Hello, World")

ac = AuthenticatedClient(URL, "gackstestuser.pkey", "gackstestuser.gid")
print "HTTPS gidNoop:", ac.gidNoop("Hello, World")

print
print "*** testing some exception handling: ***"

bc = BaseClient(URL)
print "HTTP typeError:",
try:
    result = bc.server.typeError()
    print result
except Exception, e:
    print ''.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))

print "HTTP badrequesthash:",
try:
    result = bc.server.badRequestHash()
    print result
except:
    print ''.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))

