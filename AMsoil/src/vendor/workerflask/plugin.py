from amsoil.core import pluginmanager as pm


def setup():
    # setup config items
    config = pm.getService("config")
    config.install("workerflask.dbpath", "deploy/worker.db", "Path to the worker's database (if relative, AMsoil's root will be assumed).")
    
    import workersflask as worker_package
    print "******************************", worker_package
    pm.registerService('workerflask', worker_package)
