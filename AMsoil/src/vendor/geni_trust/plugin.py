from amsoil.core import pluginmanager as pm

import amsoil.core.log
logger=amsoil.core.log.getLogger('genitrust')

import geniutil


def setup():
    
    pm.registerService("geniutil", geniutil)

    # view certificates with: openssl x509 -in ca_cert -text -noout
    # or use mac osx's Keychain Access (go into "Keychain Access"-Menu and use the Cerificate Assistant)
    # infer public key from private key for testing: openssl rsa -in mykey.pem -pubout
    
    # creates a self-signed CA cert including a new key pair
    ca_c,ca_pu,ca_pr = geniutil.create_certificate("urn:publicid:IDN+eict.de+authority+sa", is_ca=True, email="auth@example.com")

    # creates a user cert with a new key pair
    u_c,u_pu,u_pr = geniutil.create_certificate("urn:publicid:IDN+eict:de+user+tom", issuer_key=ca_pr, issuer_cert=ca_c, email="tom@example.com")
    
    # creates a user cert with a given public key
    u2_c,u2_pu,u2_pr = geniutil.create_certificate("urn:publicid:IDN+eict:de+user+manfred", issuer_key=ca_pr, issuer_cert=ca_c, public_key=u_pu, email="manni@example.com")

    logger.info(">>> CERT <<<\n %s>>> PUB <<<\n %s>>> PRIV <<<\n %s" % (u2_c,u2_pu,u2_pr))
    
    # import ext.geni
    # from ext.geni.util import cert_util as gcf_cert_util
    #
    # # setup config items
    # # config = pm.getService("config")
    # # config.install("worker.dbpath", "deploy/worker.db", "Path to the worker's database (if relative, AMsoil's root will be assumed).")
    # 
    # TMP_PATH = '/Users/motine/Documents/Ofelia/devel/test/cert' # I dont want to use tempfile, so I can look at the files (need persistant files)
    # import os.path
    # 
    # # TEST: create key-pair
    # from ext.sfa.trust.certificate import Keypair
    # kp = Keypair()
    # kp.create()
    # kp.load_from_file() # from pem
    # kp.save_to_file() # as pem
    # kp.load_from_string() # from pem
    # logger.info("private key PEM: %s" % (kp.as_pem(),))
    # logger.info("public key DER: %s" % (kp.get_pubkey_string(),))
    # 
    # # TEST: load key-pair
    # 
    # # --------------------------------------------------
    # # create a self signed CA cert
    # ca_gid, ca_keys = gcf_cert_util.create_cert("urn:publicid:IDN+eict.de+authority+sa", ca=True, email="auth@example.com");
    # logger.info("CA private key PEM: %s" % (ca_keys.as_pem(),))
    # logger.info("CA CRT: %s" % (ca_gid.save_to_string(),))
    # ca_keys.save_to_file(os.path.join(TMP_PATH, 'ca_key.pem'))
    # ca_gid.save_to_file(os.path.join(TMP_PATH, 'ca_cert.crt')) 
    # 
    # 
    # # --------------------------------------------------
    # # TEST: create user cert signed by a CA cert (incl. a new keypair)
    # 
    # user_gid, user_keys = gcf_cert_util.create_cert("urn:publicid:IDN+eict.de+user+motine", issuer_key=ca_keys, issuer_cert=ca_gid, email="user@example.com");
    # user_keys.save_to_file(os.path.join(TMP_PATH, 'user_key.pem'))
    # user_gid.save_to_file(os.path.join(TMP_PATH, 'user_cert.crt')) # this includes the parents
    # 
    # # write the public key out (needed for the next use case)
    # user_pub_key = user_keys.get_m2_pkey().get_rsa().pem() # or user_gid.get_pubkey()
    # with open(os.path.join(TMP_PATH, 'user_pub_key.pem'), 'w') as f:
    #     f.write(user_pub_key)
    # 
    # # TEST: create user cert signed by a CA cert (with existing keypair)
    # 
    # user2_gid, user2_keys = gcf_cert_util.create_cert("urn:publicid:IDN+eict.de+user+motine", issuer_key=ca_keys, issuer_cert=ca_gid, public_key=os.path.join(TMP_PATH, 'user_key.pub'), email="user@example.com");
    # user2_keys.save_to_file(os.path.join(TMP_PATH, 'user2_key.pem'))
    # user2_gid.save_to_file(os.path.join(TMP_PATH, 'user2_cert.crt')) # this includes the parents
    
    # --------------------------------------------------
    # Notes
    # slice_gid = cert_util.create_cert(urn, self.keyfile, self.certfile, uuidarg = slice_uuid)[0]
    # def create_cert(urn, issuer_key=None, issuer_cert=None, ca=False,
    #             public_key=None, lifeDays=1825, email=None, uuidarg=None):
    # issuer_key can either be a string (filename) or a Keypair
    # issuer_certfile can either be a string (filename) or a GID
    # public_key contains the entity to sign. If None a new key is created, otherwise it must be a string)
    # --------------------------------------------------

    # create two users from different CAs
    # then verify these (one should fail, one should succeed)
    
    # TEST: get root certs
    #    self.trusted_root_files = cred_util.CredentialVerifier(ca_certs).root_cert_files

    # TEST: load cert from file
    
    # TEST: create user cred (see ch.py)
    # TEST: create slice cred (see ch.py)

    # please see ca.py
    # TEST: extract info from cert
    # see GID
    # TEST: verify cert against a trusted root
    # see GID verify chain

    # # get the cert_root
    # config = pm.getService("config")
    # cert_root = expand_amsoil_path(config.get("geniv3rpc.cert_root"))
    

    # TEST: create cred
    # TEST: extract individual entries in cred
    # TEST: verify cred against a trusted root
    # client_cert = cred.Credential(string=geni_credentials[0]).gidCaller.save_to_string(save_parents=True)
    # try:
    #     cred_verifier = ext.geni.CredentialVerifier(cert_root)
    #     cred_verifier.verify_from_strings(client_cert, geni_credentials, slice_urn, privileges)
    # except Exception as e:
    #     raise RuntimeError("%s" % (e,))
    # 
    # user_gid = gid.GID(string=client_cert)
    # user_urn = user_gid.get_urn()
    # user_uuid = user_gid.get_uuid()
    # user_email = user_gid.get_email()
    # return user_urn, user_uuid, user_email # TODO document return
