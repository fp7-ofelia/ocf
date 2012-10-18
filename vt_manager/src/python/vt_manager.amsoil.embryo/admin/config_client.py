import sys
import os.path
import xmlrpclib

ADMIN_PATH = os.path.normpath(os.path.dirname(__file__))

class SafeTransportWithCert(xmlrpclib.SafeTransport): 
    # TODO this should be changed to a config file item
    # TODO add generation of admin certificates in deploy and document it
    __cert_file = os.path.join(ADMIN_PATH, "admin-cert.pem")
    __key_file = os.path.join(ADMIN_PATH, "admin-key.pem")
    
    def make_connection(self, host): 
        host_with_cert = (host, {
            'key_file' : self.__key_file, 
            'cert_file' : self.__cert_file 
        }) 
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) 


def printConfigs(keys):
    print
    i = 0
    for key, value, desc in keys:
        print "[%02i] %s %s %s" % (i, key.ljust(20), str(value).ljust(20), desc)
        i+=1

if __name__ == '__main__':
    transport = SafeTransportWithCert()
    server = xmlrpclib.ServerProxy('https://127.0.0.1:8001/amconfig', transport=transport)
    
    while True:
        keys = server.ListConfigKeys() # reload the keys every time
        printConfigs(keys)
        userInput = raw_input("number of config item to change? ('q' for quit) ")
        print
        print '>> >> >>'
        if userInput == 'q':
            break
        try:
            itemIndex = (int(userInput))
        except:
            print 'I can not understand the number you have given me. Please speak a little clearer.'
            continue
        
        currentKey, currentValue, currentDesc = keys[itemIndex]
        print "editing: %s: %s" % (currentKey.ljust(20), currentDesc)
        if type(currentValue) is bool:
            newValue = raw_input("new value (0 for False, 1 for True): ")
        else:
            newValue = raw_input("new value [%s]: " % (str(currentValue),))

        if (newValue == ''):
            print "No value given, so not changing value"
        else:
            if type(currentValue) is int: # convert the value to the right type
                try:
                    newValue = int(newValue)
                except:
                    print "not changing the value, because it used to be a number, but I could not change your input into a number."
                    continue
            if type(currentValue) is bool:
                newValue = bool(int(newValue))
                
            print "changing value for '%s' to '%s'" % (currentKey, newValue)
            server.ChangeConfig(currentKey, newValue)

    sys.exit(0)