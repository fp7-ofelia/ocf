from geni_api.utils.xmlrpc.xmlrpc_sfa_server_proxy import SfaServerProxy
from geni_api.models.xmlrpcServerProxy import xmlrpcServerProxy as xmlrpc_model

#TODO: Do not Hack this certs
SELF_GID = "/home/user/ocf.gid"
SELF_KEY = "/home/user/ocf.pkey"
class XmlrpcManager:
	
    @staticmethod
    def connect(url):
        return SfaServerProxy(url, SELF_KEY, SELF_GID)

    @staticmethod
    def configure_server(url,gid=None):
        XmlrpcManager.add_to_trusted_roots(gid)
        conn = XmlrpcManager.connect(url)
        params = conn.GetVersion()
        XmlrpcManager.save_params(params.get('value'))

    @staticmethod
    def add_to_trusted_roots(gid):
        pass

    @staticmethod
    def save_params(params):
        print params
        urn = params.get('urn')
        hrn = params.get('hrn')
        geni_api = params.get('geni_api')
        url = params.get('geni_api_versions').get(geni_api)
        ad_rspec_version = params.get('geni_ad_rspec_versions')[0].get('type')
        request_rspec_version = params.get('geni_request_rspec_versions')[0].get('type')
       # model = xmlrpc_model(urn=urn, hrn=hrn, geni_api=geni_api, url=url, ad_rspec_version=ad_rspec_version, \
       #                      request_rspec_version=request_rspec_version)
       # model.save()


        




######
#TEST#
######

#print 'Starting Test...'
#conn = XmlrpcManager.configure_server('https://192.168.254.80:9999')
   

