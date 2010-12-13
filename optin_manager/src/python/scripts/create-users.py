'''
Created on Jun 30, 2010

@author: jnaous
'''

PASSWORD = "demo"
USERNAMES = ["demo_sardis", "demo_ganil", "demo_gardil", "demo_user"]

def run():
    from django.contrib.auth.models import User
    import os
    
    for username in USERNAMES:
        print "Creating user %s..." % username
        User.objects.create_user(username, username + "@geni.net", PASSWORD)

    print "Done"
