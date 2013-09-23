#!/usr/bin/env python

# TODO fix the order of things

import sys
import os.path
import getopt
import xmlrpclib

class SafeTransportWithCert(xmlrpclib.SafeTransport): 
    # TODO add generation of admin certificates in deploy and document it
    
    cert_path = 'unset'
    key_path = 'unset'
    
    def make_connection(self, host): 
        full_cert_path = os.path.abspath(os.path.expanduser(self.cert_path))
        full_key_path = os.path.abspath(os.path.expanduser(self.key_path))
        if not os.path.exists(full_cert_path):
            raise ValueError("The specified certificate does not exist (%s)" % (full_cert_path,))
        if not os.path.exists(full_key_path):
            raise ValueError("The specified key does not exist (%s)" % (full_key_path,))
        host_with_cert = (host, {
            'key_file' : full_key_path,
            'cert_file' : full_cert_path
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

DEFAULT_HOST_AND_PORT='127.0.0.1:8002'
#DEFAULT_HOST_AND_PORT='127.0.0.1:8001'

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser(usage = "usage: %prog [options] AM_HOST:PORT")
    parser.add_option("--list", action="store_true", help="Lists all available config items.")
    parser.add_option("--set", help="Sets the config item for the given key with the given value (KEY=VALUE).")
    parser.add_option("--interactive", action="store_true", help="Starts this client in an interactive shell mode.")
    parser.add_option("--cert", help="Specifies the certificate which is used to connect. (in PEM format, defaults to 'admin-cert.pem')", default="admin-cert.pem")
    parser.add_option("--key", help="Specifies the private key used to sign the messages sent. (in PEM format, defaults to 'admin-key.pem')", default="admin-key.pem")
    opts, args = parser.parse_args(sys.argv)

    if len(args) == 1:
        print "Assuming default host %s" % (DEFAULT_HOST_AND_PORT,)
        host_name = DEFAULT_HOST_AND_PORT
    else:
        host_name = args[0]
        if host_name.find(':') == -1:
            raise ValueError("Please specify host _and_ port.")

    transport = SafeTransportWithCert()
    server = xmlrpclib.ServerProxy("https://%s/amconfig" % (host_name,), transport=transport)
    
    if not (opts.list or opts.interactive or opts.set):
        parser.print_help()
    
    if opts.cert:
        transport.cert_path = opts.cert
    if opts.key:
        transport.key_path = opts.key
    
    if opts.list:
        keys = server.ListConfigKeys() # reload the keys every time
        print_configs(keys, False)
    
    if opts.set:
        if opts.set.find('=') == -1:
            raise ValueError("When using the --set option, please use KEY=VALUE format after.")
        selected_key, new_value = opts.set.split("=")
        
        # get the list from the server and find check if it is valid
        keys = server.ListConfigKeys()
        keys = [i for i in keys if i[0] == selected_key]
        if len(keys) != 1:
            raise ValueError("Could not find the specified key.")
        set_key(server, selected_key, keys[0][1], new_value)
        sys.exit(0)

    if opts.interactive:
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
    sys.exit(0)
