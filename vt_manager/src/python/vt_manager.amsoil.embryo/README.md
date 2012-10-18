# Installation

* Please use > Python 2.7

* Install flup `sudo easy_install flup`
* Install flask `sudo easy_install flask`
* Install flask extension `sudo easy_install Flask-XML-RPC`
* Install blinker `sudo easy_install blinker`
* Install M2Crypto `sudo easy_install M2Crypto`
* Install pika `sudo easy_install pika`

You will also need to install separately a rabbitMQ server (the only IPC provider implemented for the moment). In debian-based systems should be something like:

`apt-get install rabbitmq-server`

You can create USERNAME and PASSWORD for authentication of rabbitMQ server. SSL not yet supported. More info: http://www.rabbitmq.com/

## Plugins

* Config: Install sqlalchemy `sudo easy_install sqlalchemy`
* GENIv2RPC: Install lxml `sudo easy_install lxml`

## Server

Before configuration make sure that at least `IPC_RABBITMQ_SERVER` is correctly set in `config.py`, and the rabbitMQ server is listening there.

For the development server start `main.py` and make sure you have `DEVELOPMENT_SERVER = True` configured in `amsoil/config.py`.

For the production mode with WSGI:

* Configure nginx (include `am.nginx.conf`, see example `nginx.conf.example`)
* Restart nginx
* Set `DEVELOPMENT_SERVER = False` in `amsoil/config.py`.
* Run `generate_server_key.sh` in `deploy`
* Run `main.py` to start the WSGI server

## Configuration
* Start the server once via `main.py` (so it can create the config defaults)
* Copy a trusted user certificate (issued by the clearinghouse) to `admin` (`admin-key.pem` and `admin-cert.pem`)
* Run `config_client.py` and follow the command line
* Restart the server if you changed items which need restarting

Tip: `omni` provides setup methods for creating a clearinghouse and user certificates (see http://trac.gpolab.bbn.com/gcf/wiki/Omni).

### Nginx setup

* Run the `generate_server_key.sh` in `deploy`
* Replace the paths so it fits you setup `deploy/am.nginx.conf`
* Add the `deploy/am.nginx.conf` to you nginx config file

*Note: On Mac installed via `homebrew` find the nginx logs in `tail -f /usr/local/Cellar/nginx/1.2.2/logs/*`*

# Testing with omni

* Setup omni (including all the certificate stuff)
* Start the clearinghouse server: `python src/gcf-ch.py`
* Open new console and test the getVersion call: python src/omni.py -o -a https://localhost:8001 -t geni 2 -V 2 --debug getversion

Examples for other calls (from a shell):

    python src/omni.py -o -a https://localhost:8001 -t geni 2 -V 2 --debug getversion
    python src/omni.py -o -a https://localhost:8001 -V 2 --debug --no-compress listresources
    python src/omni.py -o -a https://localhost:8001 -V 2 --debug createsliver slicename rspec-req.xml
    python src/omni.py -o -a https://localhost:8001 -V 2 --debug deletesliver slicename
    python src/omni.py -o -a https://localhost:8001 -V 2 --debug sliverstatus slicename
    

Example RSpec for rspec-req.xml:

    <?xml version="1.0" encoding="UTF-8"?>
    <rspec type="request"
           xmlns="http://www.geni.net/resources/rspec/3"
           xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:simple="http://example.com/simple/req.xsd"
           xs:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd http://example.com/simple/ad.xsd">
    <simple:ip>192.168.1.1</simple:ip>
    <simple:ip>192.168.1.2</simple:ip>
    <simple:iprange>
        <from>192.168.1.3</from>
        <to>192.168.1.6</to>
    </simple:iprange>
    </rspec>

# Tutorial

## Plugins

Most core and custom functions of AMsoil are encapsulated in plugins. Each plugin may provide services, which encapsulate the actual functionality.
A plugin consists of the following three things:

* A `MANIFEST.json` file, specifying the services and dependencies of the plugin
* A `plugin.py` file which contains a `setup()` method for initialization and registering services
* The actual implementation of the plugin

Example for a `MANIFEST.json`:

    {
      "name" : "RPC Registry",
      "author" : "Tom Rothe",
      "author-email" : "tom.rothe@eict.de",
      "version" : 1,
      "implements" : ["rpcserver", "xmlrpc"],
      "loads-after" : ["config"],
      "requires" : []
    }

To use a plugin, add the name of the required service in the manifest file.
Use either `loads-after` if the setup method (or an import in the plugin module) requires the service.
Or use `requires` if the plugin does only need the service after initialization.
Now, get a reference to the service and call methods which are published:

    import amsoil.core.pluginmanager as pm
    xmlrpc = pm.getService('xmlrpc')
    xmlrpc.registerXMLRPC('geni2', GENIv2RPC(), '/RPC2')

Note, that methods which can be used from a plugin are usually marked with the decorator `@serviceinterface`.
Consider the following plugin implementation:

    class FlaskXMLRPC(object):
        @serviceinterface
        def registerXMLRPC(self, unique_service_name, instance, endpoint):
            ...
Which has been registered in the plugin under the name `xmlrpc`:

    import amsoil.core.pluginmanager as pm
    xmlrpc = FlaskXMLRPC(flaskserver)
    pm.registerService('xmlrpc', xmlrpc)

If you are writing your own plugins, you may bind (`registerService(...)`) basically everything to a service name.
This may be an object, class, dictionary or even a module (you get the drift).
So just create a new folder in plugins, create the manifest (be sure to put all services you implement in the `implements` section), `plugin.py` and the implementation.
Then all you need to call is `registerService(...)` in your `setup` method and annotate the things you want to be used with `@serviceinterface`.

## Who's who?

![AMsoil Architecture](https://bitbucket.org/motine/amsoil/raw/00b846bc7bf2/doc/arch.png "Architecture")

The general approach for processing a request is as follows:

* An RPC receives the request and processes the input and looks up Adapters in the AdapterRegistry.
* The AdapterRegistry can return a list of Adapters which support certain contracts regarding RPC calls.
* The Adapter then translates between the resource management and the (e.g. translating to XML).
  The AdapterRegistry is the only instance which knows about the concrete shape of a Resource and the formats a RPC wants.
* When adapting the RPC request, the Adapter asks the ResourceManagerRegistry for ResourceManagers which support the resource type which is asked for.
* The ResourceManager is a _"database"_ for Resources, so you can call find, and reserve on it.
* Finally, the Resource is concerned about the concrete handling of resources (e.g. starting, keeping allocation times).

![AMsoil Architecture Example](https://bitbucket.org/motine/amsoil/raw/54f44647fb67/doc/amsoil_example.png "Architecture Example")

You may ask, why so many indirections?
Here is why: The RPC shall only deal with communication layer stuff and the ResourceManager should offer a decent API which resembles requirements of this concrete resource type.
The actual Resource then should know how the concrete resource needs to be handled.
And finally to have ResourceManagers and RPCs work together we need a translator: Adapter.
Consider the following example:

> There is a GENI v2 RPC and an OFELIA RPC.  
> The VMResourceManager can handle XENResources and LinuxContainerResources, because their functionality is basically the same if you look from above (so no need to duplicate the code for it).  
> And then the VM-GENI Adapter and VM-OFELIA Adapter translate the RPC specific stuff, like parsing XML or fulfilling other contracts like "GENI calls start on reservation of a resource."

**Ah, by the way, each plugin is supposed to handle their own persistency and configuration should be done via the config plugin.**

## What else do I need to know?

Well, there is not much more to it. Please look at the simplified **example** in `dhcpresource`.

There is some support for **logging**, so get the service, create a logger and log:

    import amsoil.core.pluginmanager as pm
    import amsoil.core.log
    
    logger=amsoil.core.log.getLogger('myname') # actually returns a decorated instance of Python's logging.Logger, so we only get one instance per name
    logger.info("doing really cool stuff...")

We also have something for **configuration** in place. So in your plugin's setup method do the following for creating defaults for keys and use them later on:

    import amsoil.core.pluginmanager as pm
    config.Config.installConfigItem(config.ConfigItem().setKey("myplugin.prefix.name").setValue("dieter").setDesc("Name of the guy to blame."))
    # later in a method
    value = config.Config.getConfigItem("myplugin.prefix.name").getValue() # <- returns "dieter" unless the admin has changed the value via the `admin/config_client.py`

Even for **authentication** there is some support. The RPC is responsible for setting up a request per context. This context is indeed request/thread-local and does contain the following fields (let the code speak):

    @classmethod @serviceinterface def currentContext(klass):

    @property @serviceinterface def user_id(self): return aStr
    @property @serviceinterface def rpc_type(self): return aStr
    @property @serviceinterface def rpc_version(self): return aInt
    @property @serviceinterface def data(self): return aDict

To get the current user name or to add/access request data:

    context = pm.getService('context').currentContext()
    logger.info(context.user_id)
    logger.info(context.data['certificate'])

**Notification** is done via signaling and as with all plugins, the documentation should live in `notification/plugin.py`

For **authorization** there is a `policy` plugin. Some people do not like to document, so please ask them directly (Marc? Leo?).

Marc is still working on **interprocess communication**.


# TODOs

##Core
* Authorization
* Have a proxy-like concept to (load-)balance between different adapters
* Implement mutex for multi-process environments
* Refinements on the IPC core service to provide a more "notification-like" system
* Create a new core service for "background job scheduling" (e.g. manage calendarized reservation expirations)
* threadlocal storage for requestContext:
  - user_id
  - user (from authorization)
  - extend authorization user model for additional user data
  - requestData (post data or something)


##Plugins
* [] Create a plugin to talk southbound to other aggregates/resource manager (e.g. GeniClient)
* [baseresourcemanager] Improve BaseResourceManager with calendarization of resources and other common resource manager utils
* Put GENIAdapter interface in GeniRPC, which derives from Adapter in AdapterRegistry
