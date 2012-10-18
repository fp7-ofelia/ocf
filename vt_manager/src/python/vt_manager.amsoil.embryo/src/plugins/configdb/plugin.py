import amsoil.core.pluginmanager as pm

"""
Configuration Provider

You always want to create the configuration keys on plug-in instantiation - it will *not* re-create the config items if they already exists in the database.
Please see the following code for creating defaults and retrieving them ("flask.bind" and "flask.port")

Example code:
    import amsoil.core.pluginmanager as pm
    config = pm.getService("config")

    # create default configurations (if they are not already in the database)
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.bind").setValue("0.0.0.0").setDesc("IP to bind the Flask RPC to."))
    config.Config.installConfigItem(config.ConfigItem().setKey("flask.port").setValue(8001).setDesc("Port to bind the Flask RPC to."))

    # acquire configuration key values
    cBind = config.Config.getConfigItem("flask.bind").getValue() # this will yield a string (unless someone changed the value to something else)
    cPort = config.Config.getConfigItem("flask.port").getValue() # this will yield an int
    
    # get all ConfigItems and change a random one:
    list = config.Config.loadAllConfigItems()
    list[0].write('newvalue')
"""

def setup():
  import amconfigdb
  pm.registerService("config", amconfigdb)