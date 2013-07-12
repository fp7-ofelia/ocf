#!/usr/bin/env python

import sys
import os.path
import getopt
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


def print_configs(keys, show_index):
    print
    i = 0
    for key, value, desc in keys:
        pr = "\n"
        if (show_index):
            pr += "[%02i] " % (i,)
        pr += "%s=%s\n%s" % (key, str(value), desc)
        print pr
        print "---"
        i+=1

def set_key(server, key, old_value, new_value):
    if (new_value == ''):
        raise ValueError("No value given, so not changing value")
    else:
        if type(old_value) is int: # convert the value to the right type
            try:
                new_value = int(new_value)
            except:
                raise ValueError("Not changing the value, because it used to be a number, but I could not change your input into a number.")
                return
        if type(old_value) is bool:
            try:
                new_value = bool(int(new_value))
            except:
                raise ValueError("Not changing the value. Could not convert the value to 1 or 0, True or False respectivly.")
                return
                
        print "Changing value for '%s' to '%s'..." % (key, new_value)
        server.ChangeConfig(key, new_value)
        print "Changed."


def print_usage():
    print "USAGE: ./config_client.py [--list] [--interactive] [--set KEY=VALUE] AM_HOST:PORT"
    print
    print "When setting boolean VALUEs please use 1 (True) or 0 (False)."
    print "This client will connect with the certificate in called 'admin-cert.pem' / 'admin-key.pem' residing in this script's folder."


DEFAULT_HOST_AND_PORT='127.0.0.1:8002'

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hlis:', ['help', 'list', 'interactive', 'set='])
        if opts == [] and args == []:
            raise ValueError("Please specify an option.")

        if len(args) == 0:
            print "Assuming default host %s" % (DEFAULT_HOST_AND_PORT,)
            host_name = DEFAULT_HOST_AND_PORT
        else:
            host_name = args[0]
            if host_name.find(':') == -1:
                raise ValueError("Please specify host _and_ port.")

        transport = SafeTransportWithCert()
        server = xmlrpclib.ServerProxy("https://%s/amconfig" % (host_name,), transport=transport)
        
        for option, opt_arg in opts:
            if option in ['-h', '--help']:
                print_usage()
                sys.exit(0)
            if option in ['-l', '--list']:
                keys = server.ListConfigKeys() # reload the keys every time
                print_configs(keys, False)
                sys.exit(0)
            if option in ['-i', '--interactive']:
                while True:
                    keys = server.ListConfigKeys() # reload the keys every time
                    print_configs(keys, True)
                    user_input = raw_input("Number of config item to change? ('q' for quit) ")
                    print
                    print '>> >> >>'
                    if user_input == 'q':
                        break
                    try:
                        item_index = (int(user_input))
                    except:
                        print 'I can not understand the number you have given me. Please speak a little clearer.'
                        continue
        
                    key, current_value, desc = keys[item_index]
                    if type(current_value) is bool:
                        new_value = raw_input("new value [0 for False, 1 for True]: ")
                    else:
                        new_value = raw_input("new value [%s]: " % (str(current_value),))

                    try:
                        set_key(server, key, current_value, new_value)
                    except Exception as e:
                        print str(e)
                sys.exit(0)
                    
            if option in ['-s', '--set']:
                if not opt_arg:
                    raise ValueError("When using the --set option, please add an argument after")
                if opt_arg.find('=') == -1:
                    raise ValueError("When using the --set option, please use KEY=VALUE format after.")
                selected_key, new_value = opt_arg.split("=")
                
                # get the list from the server and find check if it is valid
                keys = server.ListConfigKeys()
                keys = [i for i in keys if i[0] == selected_key]
                if len(keys) != 1:
                    raise ValueError("Could not find the specified key.")
                set_key(server, selected_key, keys[0][1], new_value)
                sys.exit(0)
    except getopt.GetoptError as err: # getopt.GetoptError
        print "ERROR: %s" % (err,)
        print_usage()
        sys.exit(2)

    sys.exit(0)
