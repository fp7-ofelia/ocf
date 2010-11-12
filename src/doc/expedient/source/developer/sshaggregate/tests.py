import getpass, os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from sshaggregate.views import aggregate_add_servers, aggregate_crud
from sshaggregate.models import SSHAggregate

class Tests(TestCase):
    def setUp(self):
        self.su = User.objects.create_superuser(
            "su", "su@stanford.edu", "password")
        
        self.client.login(username="su", password="password")
    
    def test_add_aggregate(self):
        self.assertEqual(SSHAggregate.objects.count(), 0)
        f = open(os.path.expanduser("~/.ssh/id_rsa"))
        pkey = f.read()
        f.close()
        response = self.client.post(
            reverse(aggregate_crud),
            data=dict(
                name="Test Aggregate",
                description="Aggregate on localhost",
                location="right here",
                admin_username=getpass.getuser(),
                private_key=pkey,
            ),
        )
        self.assertEqual(SSHAggregate.objects.count(), 1)
        self.assertRedirects(
            response, reverse(aggregate_add_servers, args=[1]))
        
        response = self.client.post(
            reverse(aggregate_crud),
            data={
                "form-0-ip_address": "127.0.0.1",
                "form-0-ssh_port": "22",
                "form-0-resource_ptr": "1",
            },
        )
        
        self.assertEqual(SSHServer.objects.count(), 1)
        self.assertRedirects(
            response, reverse(aggregate_add_servers, args=[1]))
        