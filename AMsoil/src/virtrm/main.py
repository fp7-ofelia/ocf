import sys
import getopt

from amsoil import config
from amsoil.core import pluginmanager as pm

def print_usage():
    print "USAGE: ./main.py [--help] [--worker]"
    print
    print "When no option is specified, the server will be started."
    print
    print "  --help    Print this help message."
    print "  --worker  Starts the worker process instead of the RPC server."

def main():
    # load plugins
    pm.init(config.PLUGINS_PATH)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hw', ['help', 'worker'])
    except getopt.GetoptError as e:
        print "Wrong arguments: " + str(e)
        print
        print_usage()
        return
    for option, opt_arg in opts:
        if option in ['-h', '--help']:
            print_usage()
            sys.exit(0)
        if option in ['-w', '--worker']:
            worker = pm.getService('worker')
            worker.WorkerServer().runServer()
            sys.exit(0)
    
    rpcserver = pm.getService('rpcserver')
    rpcserver.runServer()

if __name__ == "__main__":
    main()
