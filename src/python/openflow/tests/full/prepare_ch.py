'''
Created on May 19, 2010

@author: jnaous
'''
import sys
from os.path import join, dirname
PYTHON_DIR = join(dirname(__file__), "../../../")
sys.path.append(PYTHON_DIR)

def main(argv):
    from expedient.common.tests.commands import call_env_command, Env

    proj_dir, ch_host, ch_username, ch_passwd, om_host, om_port = argv
    
    # flush the CH DB and load up the CH environment
    call_env_command(proj_dir, "flush", interactive=False)
    ch_env = Env(proj_dir)
    ch_env.switch_to()
    
    from openflow.plugin.models import OpenFlowAggregate
    from expedient.common.xmlrpc_serverproxy.models import \
        PasswordXMLRPCServerProxy

    # Add the OM
    proxy = PasswordXMLRPCServerProxy.objects.create(
        username=ch_username,
        password=ch_passwd,
        url="https://%s:%s/xmlrpc/xmlrpc/" % (
            om_host, om_port,
        ),
        verify_certs = False,
    )

    # test availability
    if not proxy.is_available:
        raise Exception("Problem: Proxy not available")

    # Add aggregate
    of_agg = OpenFlowAggregate.objects.create(
        name="Test OpenFlowAggregate",
        description="This is the test OF Aggregate",
        location="America",
        client=proxy,
    )

    err = of_agg.setup_new_aggregate(ch_host)
    if err:
        raise Exception("Error setting up aggregate: %s" % err)

    ch_env.switch_from()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])