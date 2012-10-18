"""
The notification plugin aims to provide a communication service between
plugins and other elements from the system. 

The notification plugin directly provides with a simple interface through
the NotificationCenter class, which counts with a simple method to
get a signal instance:

NotificationCenter.getSignal(name = None)

notification plugin's signals are objects wrapping Signal objets inherited
from Blinker (http://discorporate.us/projects/Blinker/). The wrapped
resulting signal provides a unicast/multicast modifiable behaviour for the
signal.

the signal interface is directly provided by Blinker. At the moment 
notification plugin only ensure support for the following Signal calls:

-Signal.disableMulticast()          => disables the Multicast (multiple 
                                    receivers for the signal) capacity.
-Signal.connect(subscriber)         => register the subscriber (i.e, 
                                    class method) to receive the signal.
-Signal.send(sender)                => sends the signal to its receivers
                                    with "sender" as sender.
-Signal.send(sender, datakey = data)=> same that previous case but sending
                                    also data, which will be in a dictio-
                                    nary {'datakey':data}
-Signal.receivers                    => returns the receivers objects
                                    subscribed to the signal.


"""

import amsoil.core.pluginmanager as pm

def setup():
    from notificationcenter import NotificationCenter
    pm.registerService('notification', NotificationCenter)
