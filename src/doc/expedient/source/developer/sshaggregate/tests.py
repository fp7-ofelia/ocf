import getpass, os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from expedient.common.permissions.models import ExpedientPermission
from expedient.clearinghouse.project.models import Project
from expedient.common.tests.client import test_get_and_post_form
from sshaggregate.views import aggregate_add_servers, aggregate_crud
from sshaggregate.models import SSHAggregate, SSHServer

class Tests(TestCase):
    
    CREATED_USER_FNAME = "/tmp/created_user"
    DELETED_USER_FNAME = "/tmp/deleted_user"
    PUBKEY_USER_FNAME = "/tmp/pubkey_user"
    
    def setUp(self):
        self.su = User.objects.create_superuser(
            "su", "su@stanford.edu", "password")
        
        ExpedientPermission.objects.disable_checks()
        
        for f in Tests.CREATED_USER_FNAME, Tests.DELETED_USER_FNAME,\
        Tests.PUBKEY_USER_FNAME:
            if os.access(f, os.F_OK):
                os.unlink(f)
        
        self.client.login(username="su", password="password")
        
    def tearDown(self):
        for f in Tests.CREATED_USER_FNAME, Tests.DELETED_USER_FNAME,\
        Tests.PUBKEY_USER_FNAME:
            if os.access(f, os.F_OK):
                os.unlink(f)

        ExpedientPermission.objects.enable_checks()
    
    def test_add_aggregate(self):
        self.assertEqual(SSHAggregate.objects.count(), 0)
        
        # Get the ssh key for the local user and use that.
        f = open(os.path.expanduser("~/.ssh/id_rsa"))
        pkey = f.read()
        f.close()
        
        # Add the aggregate
        response = test_get_and_post_form(
            self.client,
            url=reverse(aggregate_crud),
            params=dict(
                name="Test Aggregate",
                description="Aggregate on localhost",
                location="right here",
                admin_username=getpass.getuser(),
                private_key=pkey,
                add_user_command="echo %(username)s >> " +
                    Tests.CREATED_USER_FNAME,
                del_user_command="echo %(username)s >> " +
                    Tests.DELETED_USER_FNAME,
                add_pubkey_user_command="echo '%(pubkey)s' >> " +
                    Tests.PUBKEY_USER_FNAME,
            ),
        )
        self.assertEqual(SSHAggregate.objects.count(), 1)
        
        next_url = reverse(aggregate_add_servers, args=[1])
        self.assertRedirects(
            response, next_url)
        
        # Add the localhost as a server
        response = test_get_and_post_form(
            self.client,
            url=next_url,
            params={
                "form-0-name": "localhost",
                "form-0-ip_address": "127.0.0.1",
                "form-0-ssh_port": "22",
            },
        )
        
        self.assertRedirects(
            response, reverse(aggregate_add_servers, args=[1]),
            msg_prefix="Response was %s" % response)
        self.assertEqual(SSHServer.objects.count(), 1)
        
    def test_create_delete_slice(self):
        # Add the aggregate
        self.test_add_aggregate()
        agg = SSHAggregate.objects.all()[0]
        
        # Create the project
        self.client.post(
            reverse("project_create"),
            data=dict(name="Test Project", description="Blah blah"),
        )
        project = Project.objects.get(name="Test Project")

        # Add the aggregate to the project
        url = reverse("project_add_agg", args=[project.id])
        response = self.client.post(
            path=url,
            data={"id": agg.id},
        )
        
        self.assertTrue(project.aggregates.count() == 1)
        
        self.assertRedirects(response, url)
        
        # Create the slice
        self.client.post(
            reverse("slice_create", args=[project.id]),
            data=dict(
                name="Test Slice",
                description="Blah blah",
            )
        )
        slice = Slice.objects.get(name="Test Slice")
        
        # Add the aggregate to the slice
        slice_add_agg_url = reverse("slice_add_agg", args=[slice.id])
        response = self.client.post(
            path=slice_add_agg_url,
            data={"id": agg.id},
        )
        
        self.assertRedirects(response, slice_add_agg_url)
        
        self.assertEqual(
            slice.aggregates.count(), 1,
            "Did not add aggregate to slice.")
        
        # Create a sliver
        server = SSHServer.objects.all()[0]
        SSHServerSliver.objects.create(resource=server, slice=slice)
        
        # Create the SSHSliceInfo
        f = open(os.path.expanduser("~/.ssh/id_rsa.pub"))
        pkey = f.read()
        f.close()
        SSHSliceInfo.objects.create(slice=slice, public_key=pkey)
        
        # Start the slice
        self.client.post(reverse("slice_start", args=[slice.id]))
        
        # Check that the add command was executed correctly
        f = open(Tests.CREATED_USER_FNAME, "r")
        username = f.read()
        f.close()
        self.assertEqual(
            username, self.su.username,
            "Add user command not executed correctly. Expected to find '%s' "
            "in %s, but found '%s' instead."
            % (self.su.username, Tests.CREATED_USER_FNAME, username))
        
        # check that the add pub key command executed correctly
        f = open(Tests.PUBKEY_USER_FNAME, "r")
        pubkey = f.read()
        f.close()
        self.assertEqual(
            username, self.su.username,
            "Add pub key command not executed correctly. Expected to find "
            "'%s' in %s, but found '%s' instead."
            % (pkey, Tests.PUBKEY_USER_FNAME, pubkey))
        
        # Stop the slice
        self.client.post(reverse("slice_stop", args=[slice.id]))
        
        # Check that the del user command executed correctly
        f = open(Tests.DEL_USER_FNAME, "r")
        username = f.read()
        f.close()
        self.assertEqual(
            username, self.su.username,
            "Del user command not executed correctly. Expected to find '%s' "
            "in %s, but found '%s' instead."
            % (self.su.username, Tests.DELETED_USER_FNAME, username))
        
