import getpass, os
import re
from StringIO import StringIO
from paramiko.rsakey import RSAKey
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.models import ExpedientPermission
from expedient.clearinghouse.project.models import Project
from expedient.common.tests.client import test_get_and_post_form
from sshaggregate.views import aggregate_add_servers, aggregate_crud
from sshaggregate.models import SSHAggregate, SSHServer, SSHServerSliver,\
    SSHSliceInfo

# Tests class
class Tests(TestCase):
    # start constants
    CREATED_USER_FNAME = "/tmp/created_user"
    '''Where do we store the created user's username?'''
    DELETED_USER_FNAME = "/tmp/deleted_user"
    '''Where do we store the deleted user's username?'''
    PUBKEY_USER_FNAME = "/tmp/pubkey_user"
    '''Where do we store the created user's public key?'''
    
    TEST_SSH_KEY_NAME = "id_rsa_sshaggregate"
    TEST_KEY_COMMENT = "ssh_aggregate_test_key"
    # end
    def create_test_ssh_key(self):
        self.test_key = RSAKey.generate(1024)
        self.test_pubkey = "\nssh-rsa %s %s\n" % \
            (self.test_key.get_base64(), Tests.TEST_KEY_COMMENT)
        f = open(os.path.expanduser("~/.ssh/authorized_keys"), "a")
        f.write(self.test_pubkey)
        f.close()
        
    def delete_test_ssh_key(self):
        f = open(os.path.expanduser("~/.ssh/authorized_keys"), "r")
        auth_keys = f.read()
        f.close()
        new_auth_keys = re.sub(
            r"\n.*%s\n" % Tests.TEST_KEY_COMMENT,"", auth_keys)
        f = open(os.path.expanduser("~/.ssh/authorized_keys"), "w")
        f.write(new_auth_keys)
        f.close()

    def setUp(self):
        # create local user
        self.su = User.objects.create_superuser(
            "su", "su@stanford.edu", "password")
        # end
        
        # disable permissions
        ExpedientPermission.objects.disable_checks()
        # end
        
        # delete existing temp files
        for f in Tests.CREATED_USER_FNAME, Tests.DELETED_USER_FNAME,\
        Tests.PUBKEY_USER_FNAME:
            if os.access(f, os.F_OK):
                os.unlink(f)
        # end
        
        # create ssh key
        self.create_test_ssh_key()
        # end
        
        # login user
        self.client.login(username="su", password="password")
        # end
        
    def tearDown(self):
        for f in Tests.CREATED_USER_FNAME, Tests.DELETED_USER_FNAME,\
        Tests.PUBKEY_USER_FNAME:
            if os.access(f, os.F_OK):
                os.unlink(f)

        self.delete_test_ssh_key()

        ExpedientPermission.objects.enable_checks()
    
    # add aggregate tests
    def test_add_aggregate(self):
        # end
        
        # check nothing is there
        self.assertEqual(SSHAggregate.objects.count(), 0)
        # end
        
        # get private key as string
        pkey_f = StringIO()
        self.test_key.write_private_key(pkey_f)
        pkey = pkey_f.getvalue()
        pkey_f.close()
        # end
        
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
                add_user_command="sh -c 'echo %(username)s >> " +
                    Tests.CREATED_USER_FNAME + "'",
                del_user_command="sh -c 'echo %(username)s >> " +
                    Tests.DELETED_USER_FNAME + "'",
                add_pubkey_user_command="sh -c 'echo %(pubkey)s >> " +
                    Tests.PUBKEY_USER_FNAME + "'",
            ),
        )
        self.assertEqual(SSHAggregate.objects.count(), 1)
        # end
        
        # where do we go next?
        next_url = reverse(aggregate_add_servers, args=[1])
        self.assertRedirects(
            response, next_url)
        # end
        
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
        # end
        
        # check that localhost added
        self.assertRedirects(
            response, reverse(aggregate_add_servers, args=[1]),
            msg_prefix="Response was %s" % response)
        self.assertEqual(SSHServer.objects.count(), 1)
        # end
        
    # slice tests
    def test_create_delete_slice(self):
        # end
        
        # Add the aggregate
        self.test_add_aggregate()
        agg = SSHAggregate.objects.all()[0]
        # end
        
        # Create the project
        self.client.post(
            reverse("project_create"),
            data=dict(name="Test Project", description="Blah blah"),
        )
        project = Project.objects.get(name="Test Project")
        # end

        # Add the aggregate to the project
        url = reverse("project_add_agg", args=[project.id])
        response = self.client.post(
            path=url,
            data={"id": agg.id},
        )
        self.assertTrue(project.aggregates.count() == 1)
        self.assertRedirects(response, url)
        # end
        
        # Create the slice
        self.client.post(
            reverse("slice_create", args=[project.id]),
            data=dict(
                name="Test Slice",
                description="Blah blah",
            )
        )
        slice = Slice.objects.get(name="Test Slice")
        # end
        
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
        # end
        
        # Create a sliver
        server = SSHServer.objects.all()[0]
        SSHServerSliver.objects.create(resource=server, slice=slice)
        # end
        
        # Create the SSHSliceInfo
        SSHSliceInfo.objects.create(
            slice=slice, public_key=self.test_pubkey)
        # end
        
        # Start the slice
        self.client.post(reverse("slice_start", args=[slice.id]))
        # end
        
        # Check that the add command was executed correctly
        self.assertTrue(os.access(Tests.CREATED_USER_FNAME, os.F_OK))
        f = open(Tests.CREATED_USER_FNAME, "r")
        username = f.read()
        f.close()
        self.assertEqual(
            username.strip(), self.su.username,
            "Add user command not executed correctly. Expected to find '%s' "
            "in %s, but found '%s' instead."
            % (self.su.username, Tests.CREATED_USER_FNAME, username))
        # end
        
        # check that the add pub key command executed correctly
        f = open(Tests.PUBKEY_USER_FNAME, "r")
        pubkey = f.read()
        f.close()
        self.assertEqual(
            username.strip(), self.su.username,
            "Add pub key command not executed correctly. Expected to find "
            "'%s' in %s, but found '%s' instead."
            % (self.test_pubkey, Tests.PUBKEY_USER_FNAME, pubkey))
        # end
        
        # Stop the slice
        self.client.post(reverse("slice_stop", args=[slice.id]))
        # end
        
        # Check that the del user command executed correctly
        f = open(Tests.DELETED_USER_FNAME, "r")
        username = f.read()
        f.close()
        self.assertEqual(
            username.strip(), self.su.username,
            "Del user command not executed correctly. Expected to find '%s' "
            "in %s, but found '%s' instead."
            % (self.su.username, Tests.DELETED_USER_FNAME, username))
        # end
