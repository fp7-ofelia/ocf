from amsoil.core import pluginmanager as pm


def setup():
    # setup config items
    config = pm.getService("config")
    config.install("virtworker.dbpath", "deploy/worker.db", "Path to the worker's database (if relative, AMsoil's root will be assumed).")
    
    import virtworkers as worker_package
    #
    # main.py --worker gets service 'worker' and initialize it.
    # The 'virtworker' service was not initilized that way.
    # Due to not change the main.py code, the new flask worker need to be registered as the 'worker' service.
    # The symlink in plugins to the worker folder has been removed, beign virtworker the only active worker.
    # Now 'virtworker' is initialized in the main.py.
    #
    #pm.registerService('virtworker', worker_package)
    #
    pm.registerService('worker', worker_package)
