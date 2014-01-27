import amsoil.core.pluginmanager as pm

def setup():
    # Setup config keys
    config = pm.getService("config")
    
    # register xmlrpc endpoint
    xmlrpc = pm.getService('xmlrpc')
    from virtrpc.virt import VirtGUIHandler
    virtgui_handler = VirtGUIHandler()
    pm.registerService('virtguihandler', virtgui_handler)
    xmlrpc.registerXMLRPC('gui', virtgui_handler, '/gui') # name, handlerObj, endpoint
