.. _dev-tutorial:

Expedient Plugin Tutorial
#########################

Expedient has two types of plugins that interact with each other:
:ref:`agg-plugins` and :ref:`ui-plugins`. This tutorial will guide through the
process of creation of both types of plugins. You'll first need to install
expedient. Please see :ref:`admin-install`.

.. _agg-plugins:

Aggregate Plugins
=================

Aggregate plugins have three main tasks:

#. Describe resources and their types to the Expedient database
#. Offer an API for other plugins to consume
#. Keep information about resources in an aggregate up-to-date

In this tutorial, we will go through the process of writing a plugin for a
very simple type of aggregate, an SSH access aggregate consisting of a set of
SSH servers. We will write an aggregate plugin that allows
users on Expedient to request SSH access to SSH servers. The admin of the
SSH aggregate will get an email with a message from the user,
information about the user, and a link on Expedient for approving or
denying the request.

If the admin approves the request, the plugin will create a login for the
user on each machine the user asks for, and add a public key provided by the
user. The plugin does that by storing a private key that can be used to login
to the server and execute the required commands.

Preliminaries
-------------

First, make sure that you have Expedient installed and that its packages are
in your python library path (PYTHONPATH environment variable). Then go through
the Django tutorial here_. Create a
package directory called :file:`sshaggregate` with the following files:

* :file:`sshaggregate/__init__.py`: An empty file
* :file:`sshaggregate/models.py`: Will contain descriptions of our resources
* :file:`sshaggregate/views.py`: Will contain the plugin's views

Also the directory hierarchy :file:`sshaggregate/templates/sshaggregate` that
will hold the templates for the plugin.

.. _here: http://www.djangoproject.com/

Writing Models
--------------

There are several models that will need to be written. Mainly, the aggregate
model, the resources' models, and any additional info that needs to be stored.

Edit the :file:`sshaggregate/models.py` so it looks like this:

.. literalinclude:: ssh_models.py
    
Let's go through the code section by section. We use paramiko in order to
communicate with our SSH servers over SSH. Paramiko is a python SSH
library.

SSHServer
.........

The first class in our module is the :class:`SSHServer` class which
extends `Resource`_ class. The `Resource`_ class defines a few common fields
and operations for resources. All resources that can be reserved must inherit
from the `Resource`_ class:

.. literalinclude:: ssh_models.py
   :lines: 13

Most importantly, the resource is related to an
`Aggregate`_ by a foreign key relationship. Take a look at the `Resource`_
class documentation before continuing.

In the :class:`SSHServer` class, we just define
some extra fields and functions. An :class:`SSHServer` instance has an IP
Address and an SSH port number:

.. literalinclude:: ssh_models.py
   :lines: 14-24

We also define two extra functions:
:func:`is_alive` and :func:`exec_command`.

.. literalinclude:: ssh_models.py
   :lines: 26,31-42,57-64

The :func:`is_alive` function pings the server and checks that it is up, while
the :func:`exec_command` function executes a command on the server using
:mod:`paramiko`.

SSHServerSliver
...............

A slice (represented by the `Slice`_ class) in Expedient is a container of
slivers of different types of resources and across different
aggregates. A sliver (represented by the generic class `Sliver`_) is the
reservation of one resource instance, and it relates the resource to the
slice. A sliver describes information about the reservation of that particular
instance. For example, if reserving a virtual machine, a sliver might describe
the CPU percentage reserved for the VM.

When an aggregate is about to create a slice across its resources, it looks at
the slice and all the slivers that are for resources it controls. It then uses
those slivers to create the slice. We will see more information on creating a
slice later.

In our example, we don't have any per sliver information, so our
:class:`SSHServerSliver` is empty:

.. literalinclude:: ssh_models.py
   :lines: 69

We could have also not created the class at
all, but it makes our code clearer. Take a look at the `Sliver`_ and `Slice`_ classes
documentation before continuing.

SSHSliceInfo
............

Some types of resources might require some per-slice info. In our example,
creating a slice requires a public key for the user, so the SSHSliceInfo class
will store that required information:

.. literalinclude:: ssh_models.py
   :lines: 71-73

SSHAggregate
............

This is the most involved class. The :class:`SSHAggregate` class extends the
generic `Aggregate`_ class. The `Aggregate`_ class defines some
functions and fields that are shared among all aggregate classes. Aggregate
plugins must always define an Aggregate_ class child.

.. literalinclude:: ssh_models.py
   :lines: 75

The :class:`SSHAggregate` class overrides the ``information`` field that
contains information about the aggregate and describes the aggregate
type. This field is used in the information page that describes the aggregate
type:

.. literalinclude:: ssh_models.py
   :lines: 76-79

It also adds a ``private_key`` and a ``username`` fields that are used to
login to the servers for administering them. These must be the same for all
servers in the aggregate:

.. literalinclude:: ssh_models.py
   :lines: 81-85

We also have three additional fields that specify the commands that should be
used for creating a user (:func:`add_user_command`), deleting a user
(:func:`del_user_command`), and adding a public key to a user
(:func:`add_pubkey_command`). These commands will be executed in an SSH shell when
creating or deleting users:

.. literalinclude:: ssh_models.py
   :lines: 84-108

We have also defined some helper functions to add and delete users from
particular server (:func:`add_user` and :func:`del_user`).

.. literalinclude:: ssh_models.py
   :lines: 135,151-159,172

These functions use the private method :func:`_op_user`. Note that in case of
error, we post a message to the user:

.. literalinclude:: ssh_models.py
   :lines: 127-132

This uses the messaging_ module and a utility function
`post_message_to_current_user`_ to post a message to the user indicating an
error has occurred. This message will be shown in the list of messages for the
user.

The :func:`check_status` method overrides the :class:`Aggregate` class's
:func:`check_status` method to also make sure that all the servers in the
aggregate are up by calling their :func:`is_alive` method.

.. literalinclude:: ssh_models.py
   :lines: 174-178

At a minimum any child that inherits from Aggregate_ must override
`start_slice`_ and `stop_slice`_ methods. Our :class:`SSHAggregate` class does
that too.

The :func:`start_slice` method calls the parent class's :func:`start_slice`
method because the parent class has some permission checking that we would
rather not copy or redo:

.. literalinclude:: ssh_models.py
   :lines: 183-184

It then gets needed information about the slice:

.. literalinclude:: ssh_models.py
   :lines: 183

And the current user:

.. literalinclude:: ssh_models.py
   :lines: 184

This line uses the threadlocals_ middleware that parses a request and stores
information about the request in local thread storage. Even though this is
usually not considered good practice, it simplifies much of the code. However,
try to minimize using it.

Then we get the slivers in the slice that are for resources in the aggregate:

.. literalinclude:: ssh_models.py
   :lines: 185,186

Note that we don't just do ``resource__aggregate=self`` because that the
resource is related to :class:`SSHAggregate`'s parent class. So we need to
compare them using ids. We could have instead done
``resource__aggregate=self.aggregate_ptr``.

Now we add the user to the server pointed to by each sliver, keeping track of
our successes for rollback in case of error:

.. literalinclude:: ssh_models.py
   :lines: 188-189

The :class:`SSHServerSliver`'s parent class has a pointer to the generic
resource. To obtain the leaf child that the sliver is pointing to, we need to
use a special function. Otherwise, ``sliver.resource`` returns an object of
type generic Resource_:

.. literalinclude:: ssh_models.py
   :lines: 191

Then we add the user, paying attention to roll back the changes in case of
errors:

.. literalinclude:: ssh_models.py
   :lines: 193-203

:func:`stop_slice` is very similar to :func:`start_slice` but a bit simpler
since we don't rollback changes in case of errors.

.. literalinclude:: ssh_models.py
   :lines: 205-213

Relationships
.............

Below we show a summary of the relationships between slices, resources, aggregates, and slivers.

.. image:: slice-aggregate-resource-relationships.png
   :align: center
   :width: 300

Each aggregate is connected to a number of resources. Each slice
is also related to a number of resources through a sliver. In our
example, an :class:`SSHAggregate` consists of a number of
:class:`SSHServer`s. A slice can have a number of
:class:`SSHServerSliver`s that are each part of an
:class:`SSHServer`.



.. _`Resource`: ../api/expedient.clearinghouse.resources.models.Resource-class.html
.. _`Aggregate`: ../api/expedient.clearinghouse.aggregate.models.Aggregate-class.html
.. _`Sliver`: ../api/expedient.clearinghouse.resources.models.Sliver-class.html
.. _`Slice`: ../api/expedient.clearinghouse.slice.models.Slice-class.html
.. _`start_slice`: ../api/expedient.clearinghouse.aggregate.models.Aggregate-class.html#start_slice
.. _`stop_slice`: ../api/expedient.clearinghouse.aggregate.models.Aggregate-class.html#stop_slice
.. _threadlocals: ../api/expedient.common.middleware.threadlocals-module.html
.. _messaging: ../api/expedient.common.messaging-module.html
.. _`post_message_to_current_user`: ../api/expedient.clearinghouse.utils-module.html#post_message_to_current_user

Writing Views and Templates
---------------------------

The next step is writing some views and HTML templates for
managing the SSH aggregate in Expedient. This includes pages for
adding the aggregate to Expedient, editing it, and deleting it.

Add Aggregate View
..................

This is the page that the user gets redirected to when she wants
to add an SSH aggregate to Expedient. First, we should sketch out
what it looks like::

                    +--------------+
    Admin Username: |              |
                    +--------------+

                    +-----------------------+
    Private Key   : |                       |
                    +-----------------------+

    
    
