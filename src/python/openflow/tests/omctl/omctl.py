from helpers import *

def main(argv):
    if (len(argv)==0 or argv[0]=="help" or argv[0]=="?"):
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
            print str(e)
            print "Invalid syntax\n %s"%help_msg("ping")
    elif (argv[0]=="create_slice"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            returned = xmlrpc_wrap_create_slice(username,password,url,argv)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("create_slice")
    elif (argv[0]=="delete_slice"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            slice_id = argv[4]
            returned = xmlrpc_wrap_delete_slice(username,password,url,slice_id)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("delete_slice")
    elif (argv[0]=="get_switches"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            returned = xmlrpc_wrap_get_switches(username,password,url)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("get_switches")
    elif (argv[0]=="get_links"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            returned = xmlrpc_wrap_get_links(username,password,url)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("get_links")
    elif (argv[0]=="change_password"):
        try:
            username = argv[1]
            password = argv[2]
            url = "%s/xmlrpc/xmlrpc/"%argv[3]
            new_password = argv[4]
            returned = xmlrpc_wrap_change_password(username,password,url,new_password)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("change_password")
    elif (argv[0]=="register_topology_callback"):
        try:
            username = argv[1]
            password = argv[2]
            om_url = "%s/xmlrpc/xmlrpc/"%argv[3]
            url= argv[4]
            cookie = argv[5]
            returned = xmlrpc_wrap_change_password(username,password,om_url,url,cookie)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("register_topology_callback")
    elif (argv[0]=="opt_in"):
        try:
            username = argv[1]
            password = argv[2]
            url = argv[3]
            project_name = argv[4]
            slice_name = argv[5]
            priority = argv[6]
            returned = http_wrap_opt_in(username,password,url,project_name,slice_name,priority)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("opt_in")
    elif (argv[0]=="opt_out"):
        try:
            username = argv[1]
            password = argv[2]
            url = argv[3]
            project_name = argv[4]
            slice_name = argv[5]
            returned = http_wrap_opt_out(username,password,url,project_name,slice_name)
            print returned
        except Exception,e:
            print str(e)
            print "Invalid syntax\n %s"%help_msg("opt_in")

            
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])