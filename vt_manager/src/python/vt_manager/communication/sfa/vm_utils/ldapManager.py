import ldap
# Configuration values for LDAP
from vt_manager.communication.sfa.sfa_config import config

class ldapManager:

    def __init__(self):
        self.server = config.LDAP_SERVER
        self.dn = config.LDAP_DN
        self.base_dn = config.LDAP_BASE_DN
        self.pw = config.LDAP_PASSWORD
        self.attrs = config.LDAP_ATTRIBUTES
        self.timeout = 25 # Seconds (ldap.timeout >= tcp.timeout)
        self.filter = config.LDAP_FILTER
        self.keystore = config.LDAP_KEYSTORE
    
    def bind(self):
        try:
            connection = ldap.initialize(self.server)
            #connection.start_tls_s()
            connection.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            connection.set_option(ldap.OPT_TIMEOUT, self.timeout)
            connection.simple_bind_s(self.dn, self.pw)
            print "Successful bind to LDAP"
            return connection
        except ldap.LDAPError as e:
            print "Bind to LDAP was unsucessful: %s" % e
            return 0
    
    # Get all projects in LDAP
    def get_all_projects(self, connection):
        try:
            result = connection.search_s(self.base_dn, ldap.SCOPE_ONELEVEL, self.filter, self.attrs)
            return result
        except:
            return 0
    
    # Get all users in all projects in LDAP
    def get_all_users(self, connection, project_list):
        try:
            for project in project_list:
                result = connection.search_s(project[0], ldap.SCOPE_ONELEVEL, self.filter, ["sshPublicKey"])
                for user in result:
                    if len(user) != 0:
                        sshdict = user[1]
                        for key in sshdict["sshPublicKey"]:
                            self.keystore.append(key)
            return 1
        except:
            return 0
    
    # Add project to LDAP
    def add_project(self, connection, cn):
        try:
            add_record = [("objectclass", ["inetorgperson"]),
                 ("cn", [cn] ),("sn", [cn])]
            connection.add_s("cn=%s,%s" % (cn, self.base_dn), add_record)
            return 1
        except:
            return 0
    
    # Add user to LDAP
    def add_user(self, connection, cn, sn, project_cn, keys):
        try:
            add_record = [('objectclass', ['inetorgperson','ldapPublicKey']),
                ('cn', [cn] ),('sn', [sn]),('sshPublicKey',keys)]
            connection.add_s("cn=%s,cn=%s," % (cn, project_cn, self.base_dn), add_record)
            return 1
        except:
            return 0
    
    # Delete project
    def del_project(self, connection, cn):
        try:
            result = connection.search_s("cn=%s,%s" % (cn, self.base_dn), ldap.SCOPE_ONELEVEL, self.filter, self.attrs)
            # Delete all users in project first
            for user in result:
                connection.delete(user[0])
            connection.delete("cn=%s,%s" % (cn, self.base_dn))
            return 1
        except:
            return 0
    
    # Check if project exists in LDAP
    def check_project_exists(self, connection, cn):
        try:
            result_id = con.search(self.base_dn, ldap.SCOPE_SUBTREE,("cn="+cn),["cn"])
            projects_list = []
            while True:
                result_type, result_data = connection.result(result_id, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        projects_list.append(result_data)
            return len(projects_list)
        except:
            return 0
    
    # Check if a user exists in a given project
    def check_user_exists(self, connection, sn, project_cn):
        try:
            result_id = con.search("cn=" + prj_cn + "," + self.base_dn, ldap.SCOPE_ONELEVEL, ("sn="+sn), ["cn","sn"])
            users_list = []
            while True:
                result_type, result_data = connection.result(result_id, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        users_list.append(result_data)
            if not users_list:
                return 0
            else:            
                return users_list[0][0][1]
        except:
            return 0
    
    # Get the number of users for a given project
    def get_number_users(self, connection, project_cn):
        try:
            result_id = connection.search_s("cn=" + prj_cn + "," + self.base_dn, ldap.SCOPE_ONELEVEL, ("cn=*"), None)
            users_list = []
            while True:
                result_type, result_data = connection.result_s(result_id, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        users_list.append(result_data)
            return len(users_list)
        except:
            return 0
    
    ##modify existing user,simpler to delete and re-add
    def modify_user(self, connection, user_info, project_cn, keys):
        try:
            result = connection.delete_s("cn=" + str(user_info["cn"][0]) + "," + "cn=" + str(prj_cn) + "," + self.base_dn)
            try:
                self.add_user(connection, str(user_info["cn"][0]), str(user_info["sn"][0]), project_cn, keys)
                return 1
            except:
                print "Error modifying user in LDAP"
        except:
            print "Error: %s" % str(sys.exc_info()[0])
            return 0
    
    # Create or modify project and users
    def add_modify_project_users(self, connection, sn, project_cn, keys):
        # Check if project exists; otherwise create one
        if self.check_project_exists(connection, project_cn) == 0:
            self.add_project(connection, project_cn)
        
        # Check if user exists in project
        result = self.check_user_exists(connection, sn, project_cn)
        if result == 0:
            # User does not exist => create
            index = self.get_number_users(connection, project_cn)
            return self.add_user(connection, "user" + str(index), sn, project_cn, keys)
        else:
            # User exists => modify
            status = self.modify_user(connection, result, project_cn, keys)
            return status

if __name__ == "__main__":
    session = ldapManager()
    connection = session.bind()
    project_list = session.get_all_projects(connection)
    session.get_all_users(connection, project_list)
