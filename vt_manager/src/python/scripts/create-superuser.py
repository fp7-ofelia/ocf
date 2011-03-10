'''
Created on Jun 30, 2010

@author: jnaous
'''

PASSWORD = "SUPERUSER_PASSWORD"
USERNAME = "SUPERUSER_USERNAME"
EMAIL = "SUPERUSER_EMAIL"

def run():
    from django.contrib.auth.models import User
    import os
    
    for env_var in [PASSWORD, USERNAME, EMAIL]:
        if env_var not in os.environ:
            print "%s environment is not set." % env_var
            return

    username = os.environ[USERNAME]
    password = os.environ[PASSWORD]
    email = os.environ[EMAIL]
    print "Creating superuser %s..." % username
    User.objects.create_superuser(username, email, password)
    print "Done"
