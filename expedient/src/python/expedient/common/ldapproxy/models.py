from django.conf import settings
import ldap
import ldap.modlist
import logging

logger = logging.getLogger("ldapproxy.models")

class LdapProxy:
    '''
    wrapper class to talk to the LDAP MASTER server.
    '''

    proxy = None

    def __init__(self):
        try:
            if settings.LDAP_MASTER_DISABLE == True: return
        except AttributeError: pass
        try:
            logger.debug("TLS AVAILABLE? %d" % (ldap.TLS_AVAIL))
	    print "LDAP SETTINGS->"+settings.LDAP_MASTER_URI
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.LDAP_MASTER_CA)
            #ldap.set_option(ldap.OPT_X_TLS_CERTFILE, settings.LDAP_MASTER_CERT)
            #ldap.set_option(ldap.OPT_X_TLS_KEYFILE, settings.LDAP_MASTER_KEY)
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, settings.LDAP_MASTER_REQCERT)
            ldap.set_option(ldap.OPT_TIMEOUT, settings.LDAP_MASTER_TIMEOUT)
            self.proxy = ldap.initialize (settings.LDAP_MASTER_URI)
            if settings.AUTH_LDAP_START_TLS:
                self.proxy.start_tls_s()
            self.proxy.simple_bind_s(settings.LDAP_MASTER_DN, settings.LDAP_MASTER_PWD)
            logger.debug ("LdapProxy.__init__: Connected to ldapserver %s as %s with CA in %s and with certificate %s and key %s" % (settings.LDAP_MASTER_URI, settings.LDAP_MASTER_DN, settings.LDAP_MASTER_CA, settings.LDAP_MASTER_CERT, settings.LDAP_MASTER_KEY))
        except ldap.LDAPError, error_message:
            logger.error ("LdapProxy.__init__: Failed connecting to ldapserver %s as %s with CA in %s and with certificate %s and key %s: %s" % (settings.LDAP_MASTER_URI, settings.LDAP_MASTER_DN, settings.LDAP_MASTER_CA, settings.LDAP_MASTER_CERT, settings.LDAP_MASTER_KEY, error_message))
            raise

    # not really possible to lock objects in de LDAP backend.
    # Howver, as expedients in different islands may compete, this becomes relevant.
    # Test 1: editing/saving several times a project, while fetching search results and (re)adding
    # object is commented out does not cause problems. Probably repeating the delete action raises
    # also a ldap.NO_SUCH_OBJECT that is silently discarded. ==> OK
    # Test 2: similar, but now deleting object is commented out. After second time, 
    # an ldap.ALREADY_EXISTS exception is raised. Either the calling code know how to deal with this
    # or user is confronted with an internal server error. ==> Good enough for now?
    # Crucial is to be careful that resubmitting does not destroy just-recedntly added data. But this 
    # should be a concern anyway.
    # Not really guarantee to be successful, but at least we try a couple of times to overcome this problem here.
    def create_or_replace (self, dn, entry):
        try:
            if settings.LDAP_MASTER_DISABLE == True: return
        except AttributeError: pass
        count = 0
        while 1:
            try:
                resultid = self.proxy.search(dn, ldap.SCOPE_BASE)
                try:
                    t, data = self.proxy.result(resultid, 1)
                    logger.debug("LdapProxy.create_or_replace: dn %s exists and is going to be deleted before being inserted again" % (dn))
                    self.proxy.delete_s(dn)
                except ldap.NO_SUCH_OBJECT:
                    pass
                logger.debug("LdapProxy.create_or_replace: adding %s [%s]" % (dn, entry))
                self.proxy.add_s(dn,ldap.modlist.addModlist(entry))
                break
            except ldap.ALREADY_EXISTS:
                count = count + 1
                if count < settings.LDAP_MASTER_RETRIES:
                    continue
                else:
                    logger.error ("LdapProxy: tried %d time to replace %s in LDAP directory" % (settings.LDAP_MASTER_RETRIES, dn))
                    raise
            except ldap.LDAPError, error_message:
                logger.error ("ldapproxy: create or replace %s with %s failed: %s" % (dn, entry, error_message))
                raise

    def delete (self, dn):
        try:
            if settings.LDAP_MASTER_DISABLE == True: return
        except AttributeError: pass
        try:
            resultid = self.proxy.search(dn, ldap.SCOPE_BASE)
            try:
                t, data = self.proxy.result(resultid, 1)
                logger.debug("LdapProxy.delete: dn %s exists and is going to be deleted" % (dn))
                self.proxy.delete_s(dn)
            except ldap.NO_SUCH_OBJECT:
                pass
        except ldap.LDAPError, error_message:
            logger.error ("ldapproxy: delete %s failed: %s" % (dn, error_message))
            raise

