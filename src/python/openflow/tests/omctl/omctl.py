from helpers import *

def main(argv):
    if (argv[0]=="help" or argv[0]=="?"):
        print help_msg()
    elif (argv[0]=="ping"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            ping_data = argv[4]
            pong_data = xmlrpc_wrap_ping(username,password,url,ping_data)
            print pong_data
        except Exception,e:
            print "Invalid syntax\n %s"%help_msg("ping")
    elif (argv[0]=="create_slice"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            returned = xmlrpc_wrap_create_slice(username,password,url,argv)
            print returned
        except Exception,e:
            print "Invalid syntax\n %s"%help_msg("create_slice")
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])