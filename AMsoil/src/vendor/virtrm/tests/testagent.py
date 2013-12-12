import time
from utils.xmlhelper import XmlHelper

def ongoing_response(action_id):
    time.sleep(10)
    response = XmlHelper.parseXmlString(xmlFileToString('/opt/ofelia/AMsoil/src/vendors/vtamrm/tests/xml/failresponse.xml'))
    response.response.provisioning.action[0].id=action_id
    response.response.provisioning.action[0].status="ONGOING"
    sendAsync(XmlHelper.craftXmlClass(response))
    return


def fail_response(action_id):
    time.sleep(10)
    response = XmlHelper.parseXmlString(xmlFileToString('/opt/ofelia/AMsoil/src/vendors/vtamrm/tests/xml/failresponse.xml'))
    response.response.provisioning.action[0].id=actionUUID
    sendAsync(XmlHelper.craftXmlClass(response))
    return
