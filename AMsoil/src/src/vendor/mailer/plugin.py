from amsoil.core import pluginmanager as pm

def setup():
    from emailer import Mailer
    pm.registerService('mailer', Mailer)
