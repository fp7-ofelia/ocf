import re
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy

class FlowVisorWrap:

    def __init__(self):
        self.__fv = FVServerProxy.objects.all()[0].proxy.api

    def get_flowspace(self):
        return self.__fv.getFlowSpace()

    def get_flow_space_by_slice(self, slice_id):
        flowspaces = self.__fv.listFlowSpace()
        output  = list()
        for fs in flowspaces:
            if slice_id in fs:
                output.append(self.parser_flow_space(fs))
        return output

    def parser_flow_space(self, fs):
        dpid = self.parse_dpid(fs)
        match = self.parse_match(fs)
        match_dict = dict()
        for key in match.keys():
            if key == "in_port":
                match_dict["in_port"] = match["in_port"]
            else:
                match_dict["headers"] = match[key]
             
        return {"dpid":dpid, "match":match_dict}

    def parse_match(self, fs):
        match = re.match(r'.*OFMatch\[(.*)\]\]\,actionsList',fs).groups(0)
        of_match = match[0]

    def parse_dpid(self, fs):
        match = re.match(r'.*dpid\=\[(.+)\]\,ruleMatch',fs).groups(0)
        return match[0] #is a tuple 

    def get_fs_headers(self, match):
        headers = dict()
        fields = match.split(",")
        for field in fields:
            key_value = field.split("=")
            headers[key_value[0]] = key_value[1]
        return headers   
