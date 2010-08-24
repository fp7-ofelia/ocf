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
* :ref:`admin-easy-install`
* :ref:`admin-git-install`

.. _admin-rpm-install:

Install Using an OpenSuSE RPM
-----------------------------
There are prebuilt OpenSuSE 11.1, 11.2, and 11.3 packages
available. To use these, you will need to add the repository
using zypper and then install the packages::

    $ sudo zypper addrepo -f http://download.opensuse.org/repo


.. _admin-manual-install:

Manual Installation
-------------------

So you wanna do it the difficult way? Alright.

Dependencies
............

The libraries that Expedient depends on are mostly included in
the package. Here are the other packages you will need:

* make
* gcc
* python
* apache >= 2.0.0
* apache-mod_ssl
* apache-mod_wsgi
* apache-mod_macro
* openssl

Building
........

To start building, just run::

    $ cd <expedient-dir>
    $ make
    $ make install

Replace :file:`<expedient-dir>` with the path to your expedient
directory. The make above is just a wrapper around the build systems
of the included libraries, and so you might get errors for missing
packages for those.

Configuration
.............

At this point, you are not yet ready to start using Expedient. You
need to configure Apache to talk to the Expedient Django application,
and you need to edit your Expedient settings.

The package includes Apache configuration files to help you use
Expedient through Apache with mod_wsgi. You will need to include the
following files in your Apache config file (usually
:file:`/etc/apache/httpd.conf`):

* :file:`<expedient-dir>/src/config/expedient/common/vhost-macros.conf`
* :file:`<expedient-dir>/src/config/expedient/clearinghouse/vhost-clearinghouse.conf`

Make sure that the :file:`vhost-macros.conf` file is included before
:file:`vhost-clearinghouse.conf`. Then edit the installed
:file:`vhost-clearinghouse.conf` file and replace the line::

    Use SimpleSSLWSGIVHost 443 expedient/clearinghouse /home/expedient/expedient

with::

    Use SimpleSSLWSGIVHost 443 expedient/clearinghouse <expedient-dir>

If your Apache configuration does not already have a ``Listen 443``
directive somewhere, then uncomment it from the
:file:`vhost-clearinghouse.conf` file. You can also change the port
that Expedient is running on by changing the ``443`` number to the new
port number you want to use. Don't forget to make sure there's a
``Listen`` directive for the new port.

.. _VMware Player: http://www.vmware.com/support/product-support/player/
.. _here: http://yuba.stanford.edu/~jnaous/expedient/expedient-vm-latest.tar.gz
.. _Flowvisor: http://www.openflowswitch.org/wk/index.php/FlowVisor
