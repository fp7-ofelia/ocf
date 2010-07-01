'''
Created on Jun 30, 2010

@author: jnaous
'''

def run():
    from django.contrib.auth.models import User
    import os
    
    if "SUPERUSER_PASSWD" not in os.environ:
        print "SUPERUSER_PASSWD environment is not set. Set this var to the\
password of the super user."
        return

    if "SUPERUSER_USERNAME" not in os.environ:
        print "SUPERUSER_USERNAME environment is not set. Set this var to the\
username of the super user."
        return
    
    if "SUPERUSER_EMAIL" not in os.environ:
        print "SUPERUSER_EMAIL environment is not set. Set this var to the\
email address of the super user."
        return
        

    username = os.environ["SUPERUSER_USERNAME"]
    password = os.environ["SUPERUSER_PASSWD"]
    email = os.environ["SUPERUSER_EMAIL"]
    print "Creating superuser %s" % username
    
    User.objects.create_superuser(username, email, password)
    
