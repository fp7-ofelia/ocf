from amsoil import config
from amsoil.core import pluginmanager as pm

def main():
    pm.init(config.PLUGINS_PATH)

    rpcserver = pm.getService('rpcserver')
    rpcserver.runServer()

if __name__ == "__main__":
    main()
