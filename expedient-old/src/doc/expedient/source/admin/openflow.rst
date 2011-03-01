Administering the Expedient OpenFlow Plugin
###########################################

There are three components in an OpenFlow Aggregate: The FlowVisor, the Opt-In
Manager, and the Expedient OpenFlow Plugin.

The Flowvisor uses rules to multiplex packets into slices.

The Opt-In Manager enforces local policies and writes rules into the FlowVisor
based on which users want to "opt into" which slices.

The Expedient OpenFlow plugin has two functions:

#. Enable Expedient to use OpenFlow Aggregates
#. Provide the `GENI Aggregate Manager API`_

.. _GENI Aggregate Manager API: http://groups.geni.net/geni/wiki/GAPI_AM_API

Adding OpenFlow Aggregates to Expedient
=======================================

To be able to add an Aggregate to Expedient, you will need to be logged in as
a user who has that permission or as a superuser. If you don't have that
permission, Expedient allows you to request it from a user who does when you
try to perform that action.

When adding an OpenFlow Aggregate, you will be telling Expedient where the
Opt-In Manager for that aggregate is and telling it about static connections
that are not automatically discovered. To add an OpenFlow aggregate from the
Expedient dashboard page, select the :guilabel:`OpenFlow Aggregate` from the
:guilabel:`Aggregate Type` drop-down menu under the :guilabel:`Aggregates`
section, and click :guilabel:`Add Aggregate`.

You will be taken to a form:

* :guilabel:`Name` is the name of the aggregate. Must be unique in Expedient.
* :guilabel:`Description` should be some information on the aggregate to help
  users know whether to use this aggregate or not.
* :guilabel:`Geographic Location` should be a location that can be found using
  Google Maps. It is the location of the aggregate.
* :guilabel:`Available` should be checked if you want to make the aggregate
  available for users.
* :guilabel:`Usage Agreement` is currently not used, but in later versions
  the plugin will require users to agree to it before using the aggregate.
* :guilabel:`Username` is the username that has been set for Expedient
  in the Opt-In manager, using the :guilabel:`Set Clearinghouse` button in the
  Opt-In manager.
* :guilabel:`Password` is the password that has been set for Expedient
  in the Opt-In manager.
* :guilabel:`Max Password Age` sets the maximum age of the password before it
  is automatically changed to a randomly generated one.
* :guilabel:`Server URL` is the URL of the Opt-In Manager's XML RPC
  interface. This is of the form
  ``https://<optin_manager.host>:<port>/xmlrpc/xmlrpc/``. The trailing slash is important.
* :guilabel:`Verify Certificates` should currently remain unchecked. Later
  versions will use this boolean to decide whether or not to verify the
  certificate chain coming back from the Opt-In Manager.

After filling the form and clicking :guilabel:`Create`, you will be taken to a
page to add static links. This is where you can add links that are not
automatically discovered by the underlying infrastructure such as links
between OpenFlow Aggregates or between the OpenFlow Aggregate and other types
of resources such as PlanetLab nodes.

You will need to click on :guilabel:`Add Link` to add the link. When done,
click on `Done`. You should see the aggregate added in the list of installed
aggregates in Expedient. If the aggregate has an OpenFlow switch, you should
see a non-zero number under the :guilabel:`Size` column and a green checkmark
under :guilabel:`Status`.

Changes in the underlying infrastructure and topology should be automatically
reflected through callbacks in Expedient.


Configuring the GENI API
========================

The GENI API interface is automatically enabled. What is missing are the
certificates of trusted clearinghouses. These certificates need to be
installed wherever Apache stores its trusted certificate list for Expedient's vhost because it is
Apache that verifies that the certificate chain for incoming users are
correct.

These certificates are installed wherever the ``GCF_X509_TRUSTED_CERT_DIR`` (see
settings_) in your :file:`localsettings.py` points. For a default
install, this would be
:file:`/etc/expedient/gcf-x509-trusted.crt`. Copy the new certificate
there. The next step is to link that certificate using its hash in the
``SSLCACertificatePath`` setting of your apache vhost file. In a default
package install, you can do this by running :command:`make` in :file:`/etc/expedient/apache/ca-certs`. You will also need to
restart Apache. *IMPORTANT*: The Makefile assumes that the certificates you
add all have a ``.crt`` extension. Only certificate files with that extension
work (a rename is sufficient).

The XMLRPC URL for the GENI API is of the form
``https://<expedient.host>:<port>/openflow/gapi/``.
The trailing slash is important.

.. _settings: http://yuba.stanford.edu/~jnaous/expedient/docs/api/expedient.clearinghouse.defaultsettings.gcf-module.html
