========
OVERVIEW
========

OFELIA Control Framework (OCF) is a set of software tools for testbed
management. It controls experimentation life-cycle; reservation,
instantiation, configuration, monitoring and uninistantiation.

Features:

Full software stack: frontend, clearinghouse and resources managers
(AMs) Support for mangement of Openflow, Virtual Machines (currently XEN)
and Emulab resources.
OCF is currently deployed in OFELIA FP7 project testbed, the European
Openflow testbed. The ideas behind its architecture are heavily influenced
by the experience of other testbed management tools and GENI architectural
concepts. Take a look at Overview section for more details.


==============
INSTALLING OCF
==============

1. Requirements
---------------

* One (or more) GNU/Linux Debian-like* system.
* One (or more) GNU/Linux Debian-like* systems to be virtualized by XEN (For VM
Manager installations only).

Note: for none Debian-like OSs you will have to manually install components since
OCF ofver-based [http://code.google.com/p/pypelib/] installation scripts only
support Debian-like OSs currently.


2. Installation for Expedient, Optin and VM Manager
---------------------------------------------------

2.1 Install mysql server

    apt-get install mysql-server

2.2 For each component create (example expedient) its own database. Use 
    strong passwords.

    mysql -p
    mysql> CREATE DATABASE expedient342;
    Query OK, 1 row affected (0.00 sec)
    mysql> grant all on expedient342.* to userName@127.0.0.1 identified by 'password';
    Query OK, 0 rows affected (0.00 sec)

2.3 If not already cloned, clone the OCF repository under folder /opt/:

    cd /opt
    git clone https://github.com/fp7-ofelia/ocf.git ofelia

    Alternatively you can download the tarball and uncompress it to /opt/

2.4 Trigger ofver [http://code.google.com/p/pypelib/] installation by 
    doing for each component:

    cd /opt/ofelia/{COMPONENT_NAME}/bin
    ./ofver install

    Where {COMPONENT_NAME} is either: expedient, optin or vt_manager
    The following actions will take place:

    * Install dependencies
    * Build Certificates (see Note 1)
    * Configure Apache
    * Set file permissions
    * Modify the localsettings.py or mySettings.py depending on the 
      component being installed
    * Populate database
    * When installation starts, ofver will ask if it is an OFELIA
      project installation or not. Select No (N) for non OFELIA testbeds.

    Note #1: When installing the component, you will need to create the
    certificates for the Certification Authority (CA) first and for the
    component later. Do not use the same Common Name (CN) for both of them,
    and make sure that the CN you use in the component later certificate
    (you can use an IP) is the same you then set in the SITE_DOMAIN field
    in the localsettings.py file.


3. Additional steps per component (Agent)
-----------------------------------------

In order for XEN servers to be managed you need to install the OFELIA XEN
Agent Daemon (OXAD) in each an every single server.

3.1 Create the directory and clone the repository:

    mkdir -p /opt/ofelia/oxa
    git clone https://github.com/fp7-ofelia/ocf.git repository

    The tree should look like:

    marc@foix:/opt/ofelia/oxa$ tree . -L 1
    └── repository
    
3.2 Trigger ofver [http://code.google.com/p/pypelib/]:

    cd /opt/ofelia/oxa/repository/vt_manager/src/python/agent/tools
    ./ofver install

Note #1: When installation starts, ofver will ask if it is an OFELIA
project installation or not, and accordingly ofver will download the
VMs templates from the proper storage.


4. Upgrade instructions
-----------------------

For all the components the upgrade procedure is the following:

    cd /opt/ofelia/{COMPONENT_NAME}/bin
    ./ofver upgrade

or for the OXAD:

    cd /opt/ofelia/oxa/repository/vt_manager/src/python/agent/tools
    ./ofver upgrade


5. Additional notes
-------------------

Please have a look to Manuals [https://github.com/fp7-ofelia/ocf/wiki/Manuals]
for further component configuration.

You can use -f force flag on ofver to force installations/upgrades. Take a look
at ./ofver -h help information for more details.


===============
FURTHER READING
===============

For more information about configuration, troubleshooting, contribution and
more please visit https://github.com/fp7-ofelia/ocf/wiki

