Administering Expedient
#######################

Expedient can be administered through a low-level built-in interface, Django's
admin interface, and through the higher level interface which is Expedient's.

But first, let's install it.

.. _admin-install:

Installing Expedient
====================

There are currently two ways to install Expedient:

* :ref:`admin-install-vm`
* :ref:`admin-manual-install`

Getting a VM image with Expedient pre-installed is by far the easiest and fastest method.

.. _admin-install-vm:

Use a Virtual Machine Image with Expedient Pre-installed
-------------------------------------------------------

You will need at least `VMware Player`_ to be able to run the
virtual machine image. It has not been tested with any other virtualization
platforms. After you install the player, download the VM from here_.

The VM has the following components:

* Flowvisor_
* An Opt-In Manager (part of the OpenFlow Aggregate)
* Expedient
* a GENI API Clearinghouse

After you have downloaded and extracted the image, open it using VMware
Player, but don't start it yet.

#. Edit the VM's settings (from the VMware Player menu) to suit your
   environment. Most importantly:

   #. Number of CPUs
   #. Networking type

      #. Use bridging mode for when you want to have the VM get an IP address
         from your campus DHCP rather than from the internal DHCP server.
      #. Use NAT mode for when you want to have th VM get an internal IP
         address and have it NAT through the host. If you choose NAT then the
         below lines will need to be added to the
         :file:`/etc/vmware/vmnet8/nat/nat.conf` file, on the VM host, following the
         ``[incomingtcp]`` section, after which the vmware service and client need
         to be restarted::

                 # Flowvisor xmlrpc port
                 8080 = <vm-ipaddr>:8080
                 # Flowvisor openflow port
                 6633 = <vm-ipaddr>:6633
                 # Expedient site
                 443 = <vm-ipaddr>:443
                 # GENI API Clearinghouse
                 8001 = <vm-ipaddr>:8001
                 # Opt-in manager
                 8443 = <vm-ipaddr>:8443

         Where the ``<vm-ipaddr>`` is the IP address of the Expedient VM.
         This will probably be something like ``192.168.53.x``. Use ifconfig
         in an Expedient VM terminal window to find the address. (For more
         information checkout VMWare Workstation's User's Manual)

#. Log into the VM with:

   * **username**: expedient
   * **password**: expedient

#. Edit :file:`/home/expedient/bin/expedient-settings`: The comments in the
   file explain the settings. Be sure to read them carefully.

#. In a terminal, run::

       $ setup-site

   This command propagates the settings in :file:`expedient-settings` to the
   rest of the installation. Be sure to run the command every time the
   settings are changed. It also generates site-specific certificates for both
   Expedient and the Flowvisor.

#. To make sure Expedient is running, open a web browser and go to
   https://localhost/ and https://localhost:8443/


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

Connecting to Apache
....................

The package includes Apache configuration files to help you use
Expedient through Apache with mod_wsgi. You will need to include the
following files in your Apache config file (usually
:file:`/etc/apache/httpd.conf`):

* :file:`<expedient-dir>/src/config/expedient/common/vhost-macros.conf`
* :file:`<expedient-dir>/src/config/expedient/clearinghouse/vhost-clearinghouse.conf`


.. _VMware Player: http://www.vmware.com/support/product-support/player/
.. _here: http://yuba.stanford.edu/~jnaous/expedient/expedient-vm-latest.tar.gz
.. _Flowvisor: http://www.openflowswitch.org/wk/index.php/FlowVisor
