'''
Created on May 11, 2010

@author: jnaous
'''

def create_req_config(ssl_dir, name, cn):
    """
    create config file for requests
    """
    
    f = open(ssl_dir+"/"+name+".cnf", 'w')
    
    f.write(
        """
        [ req ]
        default_bits           = 2048
        default_keyfile        = %s.key
        distinguished_name     = req_distinguished_name
        attributes             = req_attributes
        prompt                 = no
        output_password        =

        [ req_distinguished_name ]
        C                      = US
        ST                     = Some State
        L                      = Some Locality
        O                      = Some Organization
        OU                     = Some Organizational unit
        CN                     = %s
        emailAddress           = test@email.address

        [ req_attributes ]
        challengePassword      =
        """ % (name, cn)
    )
    
    f.close()

def create_cert(ssl_dir, keyfile, certfile, name, cn):
    """
    Create certificates for SSL.
    """
    import os, stat, subprocess
    
    print "Creating cert for %s: %s" % (name, cn)
    
    # generate server keys
    subprocess.call(["openssl", "genrsa", "-out",
                     ssl_dir+"/%s.key" % name, "2048"])
    
    # dump the request config file
    create_req_config(ssl_dir, name, cn)
    
    # generate client signing request
    subprocess.call(["openssl", "req", "-new", "-batch",
                     "-config", ssl_dir+"/%s.cnf" % name,
                     "-key", ssl_dir+"/%s.key" % name,
                     "-out", ssl_dir+"/%s.csr" % name])
    
    # create demoCA dir
    os.mkdir("demoCA")
    
    # sign the request
    subprocess.call(["openssl", "ca",
                     "-keyfile", keyfile,
                     "-cert", certfile,
                     '-policy', 'policy_anything',
                     "-outdir", ssl_dir,
                     "-out", ssl_dir+"/%s.crt" % name,
                     "-infiles", ssl_dir+"/%s.csr" % name])
    
    for ext in "crt", "key", "csr", "cnf":
        os.chmod(ssl_dir+"/%s.%s" % (name, ext), 
                 stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH
                 | stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
    
    print "Done creating cert"
        
def clean_cert(ssl_dir, name):
    """
    Delete everything related to cert for 'name'.
    """
    import os
    
    for ext in "key", "csr", "crt", "cnf":
        try:
            os.unlink(ssl_dir+"/%s.%s" % (name, ext))
        except:
            pass
