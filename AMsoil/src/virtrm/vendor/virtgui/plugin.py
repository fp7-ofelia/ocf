#import amsoil.core.pluginmanager as pm
#
#def setup():
#    # Register Virtualisation RM as a service
#    print "aaaaaaaaa"
#    from virtgui.virt import VirtGUI
#    gui = VirtGUI()
#    pm.registerService('virtgui', gui)

import amsoil.core.pluginmanager as pm

def setup():
    # Setup config keys
    #config = pm.getService("config")

    # Register Virtualisation RM as a service
    from managers import base
    # TODO Remove
    print base
    from delegate import VirtGUI
    # TODO Remove
    print VirtGUI
    delegate = VirtGUI()
    handler = pm.getService('virtguihandler')
    handler.setDelegate(delegate)

