from amsoil.core import pluginmanager as pm


def setup():
    # setup config items
    config = pm.getService("config")
    config.install("worker.dbpath", "deploy/worker.db", "Path to the worker's database (if relative, AMsoil's root will be assumed).")
    
    import workers as worker_package
    pm.registerService('worker', worker_package)
