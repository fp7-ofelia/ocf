.. _user-tutorial:

Expedient User Tutorial
=======================

In this tutorial you will do the following:

#. Create an account and get permission to create a new project (:ref:`user-tutorial-create-project`).
#. Start a slice with OpenFlow and PlanetLab resources (:ref:`user-tutorial-create-slice`).

.. _`user-tutorial-create-project`:

Create a Project
----------------

Go to the Expedient site, and click on the :guilabel:`Register` link. Fill-in your
username, email, and password. An email will be sent to you to activate your
account. Once activated, log into your account.

The home page has four sections.

* Messages: Here you can look at messages you have received, delete old ones,
  and send messages to other users.
* Aggregates: This is a list of resource aggregates that are available at
  Expedient.You can use this section to add and remove resource aggregates from
  Expedient. Resource aggregates are collections of resources that are made
  available to Expedient users.  You will need permission to add or remove
  aggregates.
* Projects: This section will list the projects of which you are a member.
* Permission Management: Here you can see a list of pending permission
  requests that others have made to you.

Users create slices within the context of projects. A project has a set of
members with different roles. Roles give users permissions to do various
actions in the project such as changing the project's information, adding
users to the project, or creating slices.

Click on the :guilabel:`Create` button in the Projects section. You will most likely
encounter a "Permission Denied" page. You will need to request the permission
from someone who can allow you to create a project. Most likely, this would be
an administrator. So select a user to make the request to (:guilabel:`Permission
Owner`), add a message that helps the administrator make a decision to allow
you to create a project, and click :guilabel:`Request`.

Once your administrator approves the request, you can go back to the homepage
and try to create the project again. Choose a simple descriptive short name,
add a description for the project, and click :guilabel:`Save`.

You will be redirected to the project's detail page where you can manage the
project.

Each project has a set of members. Each member can have multiple roles. Roles
are project-specific and they define the set of permissions a member has for
the project.

The project page has the following sections:

* Members: Shows list of members and links to add/remove/update members.
* Role Requests: When members try an action they do not have permission
  to execute, they will be redirected to a page where they can request a role
  that allows them to execute that action. This lists any roles other members
  have requested from you.
* Aggregates: This section lists the resource aggregates the project is
  allowed to use. Slices you create can only use aggregates in this list.
* Slices: List of the slices in the project.
* Roles: List of roles in the project.

Each new project gets two default roles: "researcher" and "owner". The
"researcher" role only allows the user to create and delete slices, while the
"owner" role allows a user to do everything.

Add a Member
............

Let's start by adding another member to the project. Click on :guilabel:`Add Members` in
the "Members" section. Select another user you want in the project, select
:guilabel:`researcher` role, and click on :guilabel:`Add`. The delegate checkbox can be used to
allow the user to give the roles you give him to others. 

Add Aggregates
..............

Now we should add aggregates to the project. Click on :guilabel:`Add Aggregates`. You
will see a list of the aggregates that are available in Expedient. Click the
:guilabel:`Select` button for
the ones you would like to use (choose at least one OpenFlow Aggregate and one
PlanetLab Aggregate). Some other types of aggregates might require additional
steps before an aggregate is added to the project.


.. _user-tutorial-create-slice:

Create a Slice
--------------

Now let's create a slice. Click on :guilabel:`Create Slice` in the "Slices"
section. Fill the form and click :guilabel:`Save`. The page you see is your slice's
detail page.

The :guilabel:`Management` box on the right allows you to edit basic information about
the slice, as well as start and stop the slice.


Add Aggregates
..............

As in the project detail page, you have to add aggregates to the slice in
order to be able to reserve resources from that aggregate. Select the
PlanetLab and OpenFlow aggregates to add them to the slice.

When you add an OpenFlow Aggregate, you will need to provide the URL of the
controller for your slice. All OpenFlow aggregates that you add will use the
same information, although it may be requested multiple times. So if you
change it for one, you also change it for all.

Click :guilabel:`Done`.

Add Resources
.............

To add resources to the slice, you will need to use a "User Interface
Plugin". Each such plugin specializes in some subset of resources. Click on
:guilabel:`Manage Resources` to select a plugin to add OpenFlow and PlanetLab resources.
Click on :guilabel:`Open` for the :guilabel:`HTML Table UI` plugin.

Here you'll see information about the PlanetLab and OpenFlow resources that
are available for the slice. To select a tree from all the resources present,
click on :guilabel:`Select Tree`. When you are done selecting the resources you want in
the slice, click :guilabel:`Next`.

Select FlowSpace
................

Select the flowspace that you want the controller to receive by specifying it
here. Click :guilabel:`Save` and then :guilabel:`Next` when done.

Download RSA keys
.................

Expedient generates an RSA key and uses it to create the PlanetLab slice for
you. Here you can download the provate key that you can use to login to your
PlanetLab nodes. Use the given login username to login to the PlanetLab nodes.

When you are done, click :guilabel:`Done` to go back to the detail page. You can always
come back here later to edit your slice.

Start the Slice
...............

At this point nothing has been created at the actual resource aggregates
themselves. To start your slice, click on :guilabel:`Start Slice`.

Stop the Slice
..............

Click :guilabel:`Stop Slice` to free the resources associated with your slice at the
resource aggregates.
