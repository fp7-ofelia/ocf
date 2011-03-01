.. _admin-install:

Installing Expedient
====================

There are currently two ways to install Expedient. If you're developing just a
plugin, you can use the RPM install method:

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
#. :ref:`admin-rpm-add-cron`

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

* ``ADMINS``: Set this to ``[("<admin's full name>", "<admin's
  email>")]``. See admins_.
* ``EMAIL_HOST``: Set this to the hostname of your smtp
  server. e.g. ``"smtp.gmail.com"``. You need check the other email settings
  for the defaults. See email_.
* ``DEFAULT_FROM_EMAIL``: Set this to the email address you want users to see when
  they receive mail from
  Expedient. e.g. ``"no-reply@geni.net"``. See email_
* ``GCF_BASE_NAME``: Set this to ``"<your_organization>//expedient"``. Replace
  ``<your_organization>`` with one alphanumeric word. Do not use special
  characters. e.g. ``"expedient:stanford"``. See gcf_.
* ``SITE_DOMAIN``: Set this to the fully-qualified domain name of the Expedient
  server. e.g. ``"expedient.stanford.edu"``. See site_.
* ``SITE_IP_ADDR``: Used for testing. Set to your Expedient host's IP
  address. e.g. ``"192.168.1.1"``. See openflowtests_.
* ``MININET_VMS``: Used for testing. Set to ``[("<IP address of the mininet VM>",
  ssh port num)]``. e.g. ``[("192.168.1.2", 22)]``. This will only be needed if you
  want to run the full OpenFlow tests. For more information, see
  :ref:`openflow-tests` and openflowtests_.
* ``DATABASE_USER``: Set this to the user name for the database that you want to
  use. Default should be fine for a new database
  installation. See database_.
* ``DATABASE_PASSWORD``: Set this to the password for the
  database user. See database_.

Now to make sure that the syntax is correct, do the following::

    $ PYTHONPATH=/etc/expedient python -c "import localsettings"

If you get errors, go back to localsettings.py and fix them.

.. _defaultsettings documentation: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings-module.html

.. _admins: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.admins-module.html

.. _email: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.email-module.html

.. _gcf: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.gcf-module.html

.. _site: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.site-module.html

.. _openflow: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.openflow-module.html

.. _openflowtests: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.openflowtests-module.html

.. _database: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.database-module.html

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

    $ gensslcert -h
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
the ``FW_SERVICES_EXT_TCP`` variable in
:file:`/etc/sysconfig/SuSEfirewall2` and include port
``443``. Then restart the firewall::

    $ sudo /sbin/rcSuSEfirewall2 restart

You can completely disable the firewall::

    $ sudo /sbin/rcSuSEfirewall2 stop
    $ sudo /sbin/insserv -r SuSEfirewall2_setup
    $ sudo /sbin/insserv -r SuSEfirewall2_init

Test that you can login and register new users.

You can run the internal tests by executing::

    $ PYTHONPATH=/etc/expedient expedient_manage test_expedient

Caveat: 8 of those tests will fail (some of the rpc4django tests). This
is a known bug. You can run those tests separately with::

    $ PYTHONPATH=/etc/expedient expedient_manage test rpc4django

They should pass then.

.. _admin-rpm-add-cron:

Add Expedient Cron Job:
.......................

The last thing you need to do is add a cron job that will call::

    PYTHONPATH=/etc/expedient expedient_manage run_timer_jobs

every 15 or 30 minutes, depending on the timer resolution you prefer.

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

.. _admin-git-install-dependencies:

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

Notes on Installing on Windows with Cygwin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cygwin is a little bit annoying because it is not exactly
a Linux environment. Make sure you install the following packages
using your Cygwin's setup.exe before installing the above dependencies:

* gcc
* gcc-g++
* swig
* python
* libxml2
* libxml2-devel
* libxslt
* libxlst-devel
* python-libxml2
* python-libxslt
* python-paramiko
* python-crypto

You will also need to install MySQL on the machine before continuing
and making sure mysql-config is on the path (this can be done by
simply selecting the option to add the executables to the PATH
environment variable during the MySQL installaion).

Open the cygwin bash command prompt, and execute the following:

    $ cd /usr
    $ find -name '*.dll' > /tmp/dll.list

Exit the Cygwin environment, close all cygwin processes (reboot is
preferred), then open the windows command prompt using the
:command:`cmd` command. Execute the following:

    > cd <path to cygwin>\bin
    > ash
    $ TMP=/tmp ./rebaseall -T /tmp/dll.list -v

Once done, you can proceed with installing the dependencies.

.. _admin-git-install-configure:

Configure Local Settings
........................

Run the following command to create a skeleton :file:`localsetting.py` file::

    $ cd expedient/src/python
    $ PYTHONPATH=. python expedient/clearinghouse/bootstrap_local_settings.py expedient/clearinghouse/

Then edit the newly-created :file:`expedient/clearinghouse/localsettings.py` using your favorite editor.

Take a look at the settings under defaultsettings_ to
understand all the available settings. The created settings in
:file:`localsettings.py` are the minimal ones required, and they
need to be set.

.. _defaultsettings: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings-module.html

.. _admin-git-install-database:

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

For step 1 above on an OpenSuSE installation, look at :ref:`admin-rpm-install-database`

For step 2 above, you can use an Expedient function::

    $ cd expedient/src/python
    $ PYTHONPATH=.:expedient/clearinghouse python -c 'from expedient.clearinghouse import settings; from expedient.clearinghouse.commands.utils import create_user; create_user("<DB root username>", "<DB root password>", settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME, settings.DATABASE_HOST or "localhost")'

Replace ``<DB root username>`` and ``<DB root password>`` with your
database's root username and password. This will probably be
different than your OS's root username and password.

You might get an error about the server's secret key which you
can ignore for now.

.. _admin-git-install-apache:

Configure Apache
................

Now you need to configure Apache. The instructions here assume
you have Apache installed and configured. Enable ``mod_macro``,
``mod_wsgi`` and ``mod_ssl`` according to your OS (you might need
to install them first). On OpenSuSE, you can do::

    $ sudo /usr/sbin/a2enmod wsgi
    $ sudo /usr/sbin/a2enmod ssl
    $ sudo /usr/sbin/a2enmod macro
    $ sudo /usr/sbin/a2enflag SSL

Next you will need to edit a configuration file. Open
:file:`expedient/src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf`.

In line 3, replace ``443`` with the port you want to use for Apache (note
you will need to make sure that port is enabled through the
firewall), and replace ``/home/expedient/expedient`` with the
path to your checked out Expedient tree.

Edit
:file:`expedient/src/config/expedient/common/apache/vhost-macros.conf`
and replace the ``user=...`` on line 24 with ``user=<your username``.

Then you will need to include the following files in your
:file:`httpd.conf` in order:

* :file:`expedient/src/config/expedient/common/apache/vhost-macros.conf`
* :file:`expedient/src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf`

On OpenSuSE, you can do that by::

	$ sudo ln -s expedient/src/config/expedient/common/apache/vhost-macros.conf \
	  /etc/apache2/conf.d
	$ sudo ln -s expedient/src/config/expedient/clearinghouse/apache/vhost-clearinghouse.conf \
	  /etc/apache2/vhosts.d

Make sure you have SSL working on Apache with certificates. You
can generate certificates on OpenSuSE using the
:command:`gensslcert` command. You will need to make sure that the Common Name
in the certificate produced is the fully qualified domain name of your server.
Type :command:`gensslcert -h` for options.

Note that for most testing, you won't actually use Apache, but would use
Django's internal testing webserver.

.. _admin-git-install-finalize:

Finalize the Setup
..................

Create a secret key for the server, and setup the database::

    $ cd expedient/src/python
    $ python expedient/clearinghouse/manage.py create_secret_key
    $ python expedient/clearinghouse/manage.py syncdb --noinput
    $ python expedient/clearinghouse/manage.py create_default_root

Then restart Apache.

Don't forget to open the ports in your firewall. On OpenSuSE, you
can do that by editing
the ``FW_SERVICES_EXT_TCP`` variable and include port ``443`` and any other
ports you want to allow. Then restart the firewall::

    $ sudo /sbin/rcSuSEfirewall2 restart

You can completely disable the firewall::

    $ sudo /sbin/rcSuSEfirewall2 stop
    $ sudo /sbin/insserv -r SuSEfirewall2_setup
    $ sudo /sbin/insserv -r SuSEfirewall2_init

Test that you can login and register new users.

You can run the internal tests by executing::

    $ python expedient/clearinghouse/manage.py test_expedient

You should get an `OK` at the end if all tests pass.

See :ref:`admin-rpm-add-cron` for one last step.
