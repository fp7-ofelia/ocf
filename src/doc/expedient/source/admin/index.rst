Administering Expedient
#######################

Expedient can be administered through a low-level built-in interface, Django's
admin interface, and through the higher level interface which is Expedient's.

But first, let's install it.

.. _admin-install:

Installing Expedient
====================

There are currently two ways to install Expedient:

* :ref:`admin-rpm-install`
* :ref:`admin-git-install`

.. _admin-rpm-install:

Install Using an OpenSuSE RPM
-----------------------------

You will need to do the following:

#. :ref:`admin-rpm-install-repos`
#. :ref:`admin-rpm-install-configure`
#. :ref:`admin-rpm-install-database`
#. :ref:`admin-rpm-install-apache`
#. :ref:`admin-rpm-install-finalize`

.. _admin-rpm-install-repos:

Setup Repositories and Install RPMs
...................................

There are prebuilt OpenSuSE 11.1, 11.2, and 11.3 packages
available. 

You can install them either using the single click wizard `1-Click Install`_
and skip to :ref:`admin-rpm-install-configure` or manually. If the 1-Click
installer does not start, execute the following in a terminal::

    $ sudo /sbin/OCICLI http://yuba.stanford.edu/~jnaous/expedient/expedient.ymp

To install manually, you will need to add the repositories
using zypper and then install the packages. You will also need
to install Apache and MySQL. To add the required repositories::

    $ sudo zypper addrepo -f http://download.opensuse.org/repositories/devel:/languages:/python/openSUSE_11.X python
    $ sudo zypper addrepo -f http://download.opensuse.org/repositories/devel:/languages:/perl/openSUSE_11.X perl
    $ sudo zypper addrepo -f http://download.opensuse.org/repositories/home:/jnaous:/expedient/openSUSE_11.X expedient
    $ sudo zypper addrepo -f http://download.opensuse.org/repositories/Apache:/Modules/openSUSE_11.X/ Apache:Modules
    $ sudo zypper addrepo -f http://packman.inode.at/suse/11.X packman

Replace the X with the minor version for the OpenSuSE version you're using.

Then install expedient, apache, and mysql, accepting the prompts to import the
GPG keys for the repos (option ``a``) and install the packages::

    $ sudo zypper install python-expedient expedient-servers

.. _1-Click Install: data:text/x-suse-ymu,http://yuba.stanford.edu/~jnaous/expedient/expedient.ymp

.. _admin-rpm-install-configure:

Configure Local Settings
........................

Next we'll need to configure the local settings. Open
:file:`/etc/expedient/localsettings.py`::

    $ sudo <your favorite editor> /etc/expedient/localsettings.py

You can see more information on the settings at `defaultsettings
documentation`_. Below is a list of the settings that need to be changed:

* ``ADMINS``: Set this to ``[("<admin's full name>", "<admin's email>")]``
* ``EMAIL_HOST``: Set this to the hostname of your smtp
  server. e.g. ``"smtp.gmail.com"``. You need check the other email settings
  for the defaults.
* ``DEFAULT_FROM_EMAIL``: Set this to the email address you want users to see when
  they receive mail from Expedient. e.g. ``"no-reply@geni.net"``
* ``GCF_URN_PREFIX``: Set this to ``"expedient:<your_organization>"``. Replace
  ``<your_organization>`` with one alphanumeric word. Do not use special
  characters. e.g. ``"expedient:stanford"``.
* ``SITE_DOMAIN``: Set this to the fully-qualified domain name of the Expedient
  server. e.g. ``"expedient.stanford.edu"``
* ``OPENFLOW_GAPI_RSC_URN_PREFIX``: Set this to
  ``"urn:publicid:IDB+expedient:<your_organization>:openflow"``. e.g. 
  ``"urn:publicid:IDB+expedient:stanford:openflow"``
* ``SITE_IP_ADDR``: Used for testing. Set to your Expedient host's IP
  address. e.g. ``"192.168.1.1"``
* ``MININET_VMS``: Used for testing. Set to ``[("<IP address of the mininet VM>",
  ssh port num)]``. e.g. ``[("192.168.1.2", 22)]``. This will only be needed if you
  want to run the full OpenFlow tests. For more information, see
  :ref:`openflow-tests`.
* ``DATABASE_USER``: Set this to the user name for the database that you want to
  use. Default should be fine for a new database installation.
* ``DATABASE_PASSWORD``: Set this to the password for the database user.

Now to make sure that the syntax is correct, do the following::

    $ PYTHONPATH=/etc/expedient python -c "import localsettings"

If you get errors, go back to localsettings.py and fix them.

.. _defaultsettings documentation: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings-module.html

.. _admin-rpm-install-database:

Configure MySQL
...............

If you have not installed or configured MySQL on your OpenSuSE installation
before, you'll need to do so now.

First, start MySQL::

    $ sudo /etc/init.d/mysql start

Initial MySQL Setup
^^^^^^^^^^^^^^^^^^^

If you have not previously initialized MySQL and setup the root password, type::

    $ sudo mysql_secure_installation

You will be prompted for a password. Use None (i.e. just press Enter). Follow
the prompts to create a root password and setup your server (you can just
agree to all prompts). You can leave the password blank if you want.

Add MySQL to start on reboot::

    $ sudo /sbin/insserv mysql

Expedient MySQL Setup
^^^^^^^^^^^^^^^^^^^^^

You will need to run a command to create the database user and the database
for Expedient. Execute::

    $ PYTHONPATH=/etc/expedient expedient_bootstrap_mysql --rootpassword <your_root_password>

You will get an error about the server's secret key which you can ignore for
now.

.. _admin-rpm-install-apache:

Configure Apache
................

Now you need to configure Apache. The instructions here assume you have not
configured Apache before, and this is a new installation on OpenSuSE::

    $ sudo /usr/sbin/a2enmod wsgi
    $ sudo /usr/sbin/a2enmod ssl
    $ sudo /usr/sbin/a2enflag SSL
    $ sudo ln -s /etc/expedient/apache/vhost-clearinghouse.conf /etc/apache2/vhosts.d/

Add Apache to start on reboot::

    $ sudo /sbin/insserv apache2

Now generate SSL certificates. Make sure you read the help for
:command:`gensslcert` if you need to customize the generated SSL
certificates (for example, to change the used common name)::

    $ sudo gensslcert

.. _admin-rpm-install-finalize:

Finalize the Setup
..................

Create a secret key for the server, and setup the database::

    $ sudo PYTHONPATH=/etc/expedient expedient_manage create_secret_key
    $ sudo PYTHONPATH=/etc/expedient expedient_manage syncdb --noinput
    $ sudo PYTHONPATH=/etc/expedient expedient_manage create_default_root
    $ sudo /etc/init.d/apache2 restart

Don't forget to open the ports in your firewall. You can do that by editing
the ``FW_SERVICES_EXT_TCP`` variable and include port ``443`` and any other
ports you want to allow. Then restart the firewall::

    $ sudo /sbin/rcSuSEfirewall2 restart

You can completely disable the firewall::

    $ sudo /sbin/rcSuSEfirewall2 stop
    $ sudo /sbin/insserv -r SuSEfirewall2_setup
    $ sudo /sbin/insserv -r SuSEfirewall2_init

Test that you can login and register new users.

You can run the internal tests by executing::

    $ PYTHONPATH=/etc/expedient expedient_manage test_expedient

Caveat: Some of those tests will fail (in particular rpc4django tests). This
is a known bug. You can run those tests separately with::

    $ PYTHONPATH=/etc/expedient expedient_manage test rpc4django

They should pass then.

.. _admin-git-install:

Install From Git
----------------

Installing from Git is the best way to create a development environment.

#. :ref:`admin-git-install-repo`
#. :ref:`admin-git-install-dependencies`
#. :ref:`admin-git-install-configure`
#. :ref:`admin-git-install-database`
#. :ref:`admin-git-install-apache`
#. :ref:`admin-git-install-finalize`

.. _admin-git-install-repo:

Checkout the Repository
.......................

For read-only access::

    $ git clone git://openflow.org/expedient

For read-write access, you'll need to have your public key added to gitosis, then::

    $ git clone git@openflow.org/expedient

Install Package Dependencies
............................

Expedient depends on the following non-Python packages:

* python >= 2.6
* xmlsec1
* libxmlsec1-openssl-devel

If you want to use

Expedient also depends on the following Python packages:

* setuptools
* django >= 1.2, < 1.3
* django_extensions
* django_evolution
* django-autoslug
* django-registration >= 0.7, < 0.8
* decorator
* m2crypto
* PIL
* python-dateutil
* pycrypto
* paramiko
* django-renderform
* webob
* pyOpenSSL
* pyquery
* sphinx
* pygments
* libxslt-python
* ZSI
* MySQL-python >= 1.2.1p2

If you install ``setuptools``, and you have their dependencies
installed, you can install all of these packages using ::

    $ sudo easy_install <python-package>

Configure Local Settings
........................

Run the following command to create a skeleton :file:`localsetting.py` file::

    $ cd expedient/src/python
    $ python expedient/clearinghouse/manage.py bootstrap_local_settings

Then edit the newly-created :file:`expedient/clearinghouse/localsettings.py` using your favorite editor.

Take a look at the settings under ``defaultssettings``_ to
understand all the available settings. The created settings in
:file:`localsettings.py` are the minimal ones required.

.. _``defaultsettings``: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings-module.html

Configure a MySQL Database
..........................

If you have not installed or configured MySQL on your installation
before, you'll need to do so now. Since this part of the manual
is distro agnostic, you'll need to review your distro's
documentation for installing MySQL.

You will need to do the following:

#. Install MySQL somewhere and make sure it can be accessed from
 the Expedient host.
#. Configure MySQL to allow Expedient to create its users and databases.

For step 2 above, you can use an Expedient function::

    $ cd expedient/src/python
    $  --rootpassword <your_mysql_root_password>

You will get an error about the server's secret key which you can ignore for
now.

.. _admin-git-install-apache:

Configure Apache
................

Now you need to configure Apache. The instructions here assume you have not
configured Apache before, and this is a new installation on OpenSuSE::

    $ sudo /usr/sbin/a2enmod wsgi
    $ sudo /usr/sbin/a2enmod ssl
    $ sudo /usr/sbin/a2enflag SSL
    $ sudo ln -s /etc/expedient/apache/vhost-clearinghouse.conf /etc/apache2/vhosts.d/

Add Apache to start on reboot::

    $ sudo /sbin/insserv apache2

Now generate SSL certificates. Make sure you read the help for
:command:`gensslcert` if you need to customize the generated SSL
certificates (for example, to change the used common name)::

    $ sudo gensslcert

.. _admin-rpm-install-finalize:

Finalize the Setup
..................

Create a secret key for the server, and setup the database::

    $ sudo PYTHONPATH=/etc/expedient expedient_manage create_secret_key
    $ sudo PYTHONPATH=/etc/expedient expedient_manage syncdb --noinput
    $ sudo PYTHONPATH=/etc/expedient expedient_manage create_default_root
    $ sudo /etc/init.d/apache2 restart

Don't forget to open the ports in your firewall. You can do that by editing
the ``FW_SERVICES_EXT_TCP`` variable and include port ``443`` and any other
ports you want to allow. Then restart the firewall::

    $ sudo /sbin/rcSuSEfirewall2 restart

You can completely disable the firewall::

    $ sudo /sbin/rcSuSEfirewall2 stop
    $ sudo /sbin/insserv -r SuSEfirewall2_setup
    $ sudo /sbin/insserv -r SuSEfirewall2_init

Test that you can login and register new users.

You can run the internal tests by executing::

    $ PYTHONPATH=/etc/expedient expedient_manage test_expedient
