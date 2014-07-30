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
    def addProject(self, connection, cn):
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

if __name__ == "__main__":
    session = ldapManager()
    connection = session.bind()
    project_list = session.get_all_projects(connection)
    session.get_all_users(connection, project_list)
