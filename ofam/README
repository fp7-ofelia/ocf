========
OVERVIEW
========

First of all, thanks to Nick Bastin for gracefully supplying the base for this open-source OpenFlow Aggregate Manager.
For info regarding the specific FOAM version that is developed for OFELIA, please contact me (Vasileios Kotronis).
In the case of errors/omissions in this guide I take full responsibility and welcome your feedback for improving further.

===============
INSTALLING FOAM
===============


1. Considerations
-----------------

In case a previous version of FOAM is already installed on your system (under /opt/ofelia/ofam/local), the installation script will automatically backup the contents of the /opt/ofelia/ofam/local/db and /opt/ofelia/ofam/local/etc folders and the file /opt/ofelia/ofam/local/lib/foam/ofeliasettings/vlanset.py. After the installation, it will reinstate those folders and files to their original location. The ofver script will be modified by the OFELIA team to include the installation script (together with the automated backup) in next OCF versions. Generally, this OFAM comes with three folders:

    * bin (git versioned, according to OCF structure) --> /opt/ofelia/ofam/bin
    * src (git versioned, all src files, to be modified by hand only through git) --> /opt/ofelia/ofam/src
    * local (not git versioned, created on first installation) --> /opt/ofelia/ofam/local After integration with the main ofelia branch, most of the installation functionality will be handled by the ofver tool. Next steps are only required in case you install this OFAM for the first time.


2. Installation of FOAM
-----------------------

Installation and upgrade are performed automatically by ofver as follows:

    cd /opt/ofelia/ofam/bin
    sudo ./ofver install

But if you want to install it yourself, just follow the next instructions.

2.1 Move into the OFAM code

    cd /opt/ofelia/ofam/src

2.2 Install FOAM:

    sudo python install.py

    And agree ('y') to install required packages without verification:

    Reading package lists... Done
    Building dependency tree       
    Reading state information... Done
    The following extra packages will be installed:
      libxmlsec1 libxmlsec1-openssl libxslt1.1 nginx python-dateutil python-m2crypto python-pip python-pkg-resources python-setuptools xmlsec1
    Suggested packages:
      python-distribute python-distribute-doc
    The following NEW packages will be installed:
      foam libxmlsec1 libxmlsec1-openssl libxslt1.1 nginx python-dateutil python-m2crypto python-pip python-pkg-resources python-setuptools xmlsec1
    0 upgraded, 11 newly installed, 0 to remove and 51 not upgraded.
    Need to get 1,550kB of archives.
    After this operation, 5,444kB of additional disk space will be used.
    Do you want to continue [Y/n]? 
    WARNING: The following packages cannot be authenticated!
    foam
    Install these packages without verification [y/N]? y

    If everything went OK you should see the FOAM folder (/opt/ofelia/ofam). Otherwise make sure you install previously the required packages.

2.3  Download the following root certificates and/or ant other you might need and place them all under /opt/ofelia/ofam/local/etc/gcf-ca-certs/:

    sudo wget http://www.pgeni.gpolab.bbn.com/ca-cert/pgeni.gpolab.bbn.com.pem -O /opt/ofelia/ofam/local/etc/gcf-ca-certs/pgeni.gpolab.bbn.com.pem

2.4  Rebuild the nginx CA cert bundle:

    sudo foamctl admin:bundle-certs

2.5  Remove the symlink to the default nginx site (if you're not running it intentionally):

    sudo rm /etc/nginx/sites-enabled/default

2.6  (Re)start the services

    sudo service nginx restart # (if not already running it will just start)
    sudo service foam restart  # (if not already running it will just start)

2.7  If everything went OK you should be able to:
        See FOAM running: sudo service foam status
        See it installed by now under /opt/ofelia/ofam/local (main working folder for FOAM)

2.8  Now you can use the foamctl tool/cli to control FOAM, slice-allocation etc.
        For FOAM control: just run foamctl and check the available calls.
            Note: default password is admin
        The following commands allow to access and set configuration values and are needed to begin working :
            In general, to get a configuration value: foamctl config:get-value --key ...
            In general, to set a configuration value: foamctl config:set-value --key ... --value ...
            To start with (necessary step), set FlowVisor info for your island (foamctl config:set-flowvisor-info). First make sure that FlowVisor is running, this is needed so that you can use the FlowVisor methods (like ping) later. The cli will ask the hostname (e.g. localhost), XML port (default=8080) and JSON port (default=8081) that FlowVisor listens to. For the hostname simply pinpoint the machine on which FlowVisor runs.
            Next (also necessary step), edit the geni.site-tag value as follows: foamctl config:set-value --key geni.site-tag --value fp7-ofelia.eu:ocf:SITE_DOMAIN . This is needed for the production of OFELIA-compatibe rspecs within our FOAM version, and it identifies that FOAM is installed on an OFELIA island running OCF. If this is not the case (OFELIA island), contact us for more details on how to proceed. After setting the tag, please restart foam. Note: SITE_DOMAIN is the domain you are using for identifying your particular island site.
            In case you are not sure about the arguments you can supply to each foamctl command, please check the native script at /usr/local/bin/foamctl

2.9  [Optional] Setup email configuration: note that you don't have to set a value for Reply-To: unless you want it to be different from the From: address for some reason

    foamctl config:setup-email
    Password: <admin password> 
    Admin email:                  
    SMTP Server: 
    From: 
    Reply-To:

2.10 Note: make sure port 3626 is reachable by experimenters (i.e. isn't blocked by network firewalls, iptables, etc). In case of problems, first check the log files under /opt/ofelia/ofam/local/log, especially the foam.log. If needed, rerunning the installation script (after pulling the latest git bug-fixes) will fix most major issues (and no other steps are required from your side).


===============
FURTHER READING
===============

Want to know more about FOAM?

These pages may be useful:

    MAIN FOAM home: https://openflow.stanford.edu/display/FOAM/Home
    For more configuration options: https://openflow.stanford.edu/display/FOAM/Configuration+Options
    FOAM FAQ: https://openflow.stanford.edu/display/FOAM/FAQ
    The default FOAM installation: https://openflow.stanford.edu/pages/viewpage.action?pageId=7045226
