'''
Created on Nov 9, 2010

@author: jnaous
'''
from datetime import datetime, timedelta
from django.conf import settings
from expedient.common.messaging.models import DatedMessage
from expedient.common.middleware import threadlocals
from django.contrib.auth.models import User
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.project.models import Project
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.resources.models import Sliver
from expedient.clearinghouse.roles.models import ProjectRole

def post_message_to_current_user(msg_text, sender=None,
                                 msg_type=DatedMessage.TYPE_ANNOUNCE):
    """Post a message to the user whose request is being processed.
    
    This function depends on the threadlocals middleware to find the current
    user, so it must be installed.
    
    @param msg_text: The message to post for the user.
    @type msg_text: C{str}
    @keyword sender: The message sender. Defaults to None.
    @type sender: C{django.contrib.auth.models.User}
    @keyword msg_type: The type of the message. Defaults to
        L{DatedMessage.TYPE_ANNOUNCE}.
    @type msg_type: C{str} limited to one of L{DatedMessage}.TYPE_*
    
    """
    
    user = threadlocals.get_thread_locals()["user"]
    DatedMessage.objects.post_message_to_user(
        msg_text, user, sender, msg_type)
    
def add_dummy_agg_to_test_settings(test):
    """Adds the dummy aggregate test models to the installed apps of the test.
    
    C{test} must be a child of L{expedient.common.tests.manager.SettingsTestCase}.
    
    """
    from django.conf import settings
    test.settings_manager.set(
        INSTALLED_APPS=settings.INSTALLED_APPS + \
        ["expedient.clearinghouse.aggregate.tests"],
        AGGREGATE_PLUGINS=settings.AGGREGATE_PLUGINS + \
            [("expedient.clearinghouse.aggregate.tests.models.DummyAggregate",
              "dummy_agg",
              "expedient.clearinghouse.aggregate.tests.urls"),
            ],
        DEBUG_PROPAGATE_EXCEPTIONS=True,
    )    
    

def create_test_users(test):
    # create users
    test.u1 = User.objects.create_user(
        "user1", "u@u.com", "password")
    test.u2 = User.objects.create_user(
        "user2", "u@u.com", "password")
    test.u3 = User.objects.create_user(
        "user3", "u@u.com", "password")
    
def give_test_permissions(test):
    
    create_test_users(test)
    
    # give permissions
    give_permission_to("can_add_aggregate", Aggregate, test.u1)
    give_permission_to("can_create_project", Project, test.u2)
    
def create_test_aggregates(test):

    from expedient.clearinghouse.aggregate.tests.models import DummyAggregate
    
    give_test_permissions(test)
    
    test.client.login(username=test.u1.username, password="password")
    threadlocals.push_frame(user=test.u1)
    
    test.agg1 = DummyAggregate.objects.create(
        name="Agg1",
    )
    test.agg1.create_resources()
    
    test.agg2 = DummyAggregate.objects.create(
        name="Agg2",
    )
    test.agg2.create_resources()
    
    # give permissions to use aggregates
    give_permission_to("can_use_aggregate", test.agg1, test.u2)
    give_permission_to("can_use_aggregate", test.agg2, test.u2)
    
    test.client.logout()
    threadlocals.pop_frame()

def create_test_project(test):
    
    create_test_aggregates(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # create the project
    Project.objects.all().delete()
    test_get_and_post_form(
        client=test.client,
        url=Project.get_create_url(),
        params={"name": "project name", "description": "project description"},
    )
    test.project = Project.objects.all()[0]

    test.client.logout()
    threadlocals.pop_frame()

def add_test_project_member(test):
    
    create_test_project(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # add a member
    researcher = ProjectRole.objects.get(project=test.project, name="researcher")
    test_get_and_post_form(
        client=test.client,
        url=test.project.get_member_add_url(),
        params={"user": test.u3.id, "roles": researcher.id},
    )
    
    test.assertEqual(test.project.owners.count(), 1)
    test.assertEqual(test.project.members.count(), 2)

    test.client.logout()
    threadlocals.pop_frame()
    
def add_test_aggregate_to_project(test):
    
    add_test_project_member(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # add the aggregate to the project
    test_get_and_post_form(
        client=test.client,
        url=test.project.get_agg_add_url(),
        params={"id": "%s" % test.agg1.id},
    )
    test_get_and_post_form(
        client=test.client,
        url=test.project.get_agg_add_url(),
        params={"id": "%s" % test.agg2.id},
    )
    test.assertEqual(test.project.aggregates.count(), 2)

    test.client.logout()
    threadlocals.pop_frame()
            
def create_test_slice(test):
    
    add_test_aggregate_to_project(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # create the slice
    Slice.objects.all().delete()
    
    expiration = datetime.now() + timedelta(days=settings.MAX_SLICE_LIFE - 5)
    
    test_get_and_post_form(
        client=test.client,
        url=Slice.get_create_url(proj_id=test.project.id),
        params={
            "name": "slice name",
            "description": "slice description",
            "expiration_date_0": "%s" % expiration.date(),
            "expiration_date_1": expiration.time().strftime("%H:%m:%S"),
        },
    )
    test.slice = Slice.objects.all()[0]

    test.client.logout()
    threadlocals.pop_frame()
    
def add_test_aggregate_to_slice(test):
    
    create_test_slice(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # add the aggregate to the slice
    test_get_and_post_form(
        client=test.client,
        url=test.slice.get_agg_add_url(),
        params={"id": "%s" % test.agg1.id},
    )
    test_get_and_post_form(
        client=test.client,
        url=test.slice.get_agg_add_url(),
        params={"id": "%s" % test.agg2.id},
    )
    test.assertEqual(test.slice.aggregates.count(), 2)

    test.client.logout()
    threadlocals.pop_frame()
    
def add_resources_to_test_slice(test):
    
    from expedient.clearinghouse.aggregate.tests.models import DummyResource

    add_test_aggregate_to_slice(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # add resources to the slice
    for agg in [test.agg1, test.agg2]:
        for rsc in DummyResource.objects.filter(aggregate=agg):
            Sliver.objects.create(resource=rsc, slice=test.slice)

    test.client.logout()
    threadlocals.pop_frame()
        
def start_test_slice(test):
    """Create a test setup with aggregates, users, project, and started slice.
    
    Creates two users, test.u1 and test.u2. Gives test.u1 permission to
    create aggregates. Creates two dummy aggregates with resources using u1.
    
    Gives u2 permission to create project, creates project with u2, add u1 as
    researcher member, creates a slice, add all dummy resources to slice,
    and starts it.
    
    C{test} must be a child of L{expedient.common.tests.manager.SettingsTestCase}.
    
    """
    
    add_resources_to_test_slice(test)
    
    test.client.login(username=test.u2.username, password="password")
    threadlocals.push_frame(user=test.u2)

    # start the slice
    test_get_and_post_form(
        client=test.client,
        url=test.slice.get_start_url(),
        params={},
    )
    test.slice = Slice.objects.get(pk=test.slice.pk)
    test.assertTrue(test.slice.started)

    test.client.logout()
    threadlocals.pop_frame()
    
    
