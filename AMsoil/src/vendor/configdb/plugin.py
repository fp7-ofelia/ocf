import amsoil.core.pluginmanager as pm

"""
Configuration Provider

You always want to create/install the configuration keys on plug-in instantiation - it will *not* re-create the config items if they already exists in the database.
Please see the following code for creating defaults and retrieving them ("flask.bind" and "flask.port")
The type / class of the value is preserved. Pickle is used to serialize the values.

Example code:
    import amsoil.core.pluginmanager as pm
    config = pm.getService("config")

    # create default configuration (if they are not already in the database, e.g. during setup of the plugin)
    config.install("flask.bind", "0.0.0.0", "IP to bind the Flask RPC to.")
    config.install("flask.port", 8001, "Port to bind the Flask RPC to.")

    # acquire configuration key values
    cBind = config.get("flask.bind") # this will yield a string (unless someone changed the value to something else)
    cPort = config.get("flask.port") # this will yield an int

    # set a value for a key
    config.set("flask.bind", "127.0.0.1")
    
    # get all config items as a list of hashes:
    list = config.getAll()
"""

def setup():
    import amconfigdb
    import amconfigdbexceptions
    pm.registerService("config", amconfigdb.ConfigDB())
    pm.registerService("configexceptions", amconfigdbexceptions)
