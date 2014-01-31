from foam.sfa.rspecs.versions.pgv2 import PGv2Ad, PGv2Request, PGv2Manifest

class FedericaAd (PGv2Ad):
    enabled = True
    schema = 'http://sorch.netmode.ntua.gr/ws/RSpec/ad.xsd'
    namespace = 'http://sorch.netmode.ntua.gr/ws/RSpec'

class FedericaRequest (PGv2Request):
    enabled = True
    schema = 'http://sorch.netmode.ntua.gr/ws/RSpec/request.xsd'
    namespace = 'http://sorch.netmode.ntua.gr/ws/RSpec'

class FedericaManifest (PGv2Manifest):
    enabled = True
    schema = 'http://sorch.netmode.ntua.gr/ws/RSpec/manifest.xsd'
    namespace = 'http://sorch.netmode.ntua.gr/ws/RSpec'

