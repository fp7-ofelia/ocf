import os
from openflow.optin_manager.sfa.methods.ListResources import ListResources

#cred = open('/opt/ofelia/optin_manager/src/python/openflow/optin_manager/sfa/tests/credential_procedure/topdomain.nitos.pi.user.cred','r').read()
cred = open(os.path.join(os.getenv("OCF_PATH"),"optin_manager/src/python/openflow/optin_manager/sfa/tests/credential_procedure/topdomain.nitos.pi.user.cred"),"r").read()

vt_sfa_schema_path = os.path.join(os.getenv("OCF_PATH"),"vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd")
options = {'geni_ad_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': vt_sfa_schema_path}], 'code_url': 'git://git.onelab.eu/sfa.git@sfa-2.1-23', 'geni_request_rspec_versions': [{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': vt_sfa_schema_path}], 'sfa': 2}
options = {'geni_rspec_version':{'namespace': None, 'version': '1', 'type': 'OcfVt', 'extensions': [], 'schema': vt_sfa_schema_path}}

ListResources(cred,options)

