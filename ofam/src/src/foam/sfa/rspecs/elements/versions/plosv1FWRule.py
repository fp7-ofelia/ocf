from foam.sfa.rspecs.elements.element import Element  
from foam.sfa.rspecs.elements.fw_rule import FWRule

class PLOSv1FWRule:
    @staticmethod
    def add_rules(xml, rules):
        if not rules:
            return 
        for rule in rules:
            rule_elem = xml.add_element('{%s}fw_rule' % xml.namespaces['plos'])
            rule_elem.set('protocol', rule.get('protocol'))
            rule_elem.set('port_range', rule.get('port_range'))
            rule_elem.set('cidr_ip', rule.get('cidr_ip'))
            if rule.get('icmp_type_code'):
                rule_elem.set('icmp_type_code', rule.get('icmp_type_code'))
              
    @staticmethod
    def get_rules(xml):
        rules = []
        if 'plos' in xml.namespaces: 
            for rule_elem in xml.xpath('./plos:fw_rule | ./fw_rule'):
                rule = FWRule(rule_elem.attrib, rule_elem)
                rules.append(rule)  
        return rules

