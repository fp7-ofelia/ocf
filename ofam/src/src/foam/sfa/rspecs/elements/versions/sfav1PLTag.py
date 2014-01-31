from foam.sfa.rspecs.elements.element import Element  
from foam.sfa.rspecs.elements.pltag import PLTag

class SFAv1PLTag:
    @staticmethod
    def add_pl_tag(xml, name, value):
        for pl_tag in pl_tags:
            pl_tag_elem = xml.add_element(name)
            pl_tag_elem.set_text(value)
              
    @staticmethod
    def get_pl_tags(xml, ignore=[]):
        pl_tags = []
        for elem in xml.iterchildren():
            if elem.tag not in ignore:
                pl_tag = PLTag({'tagname': elem.tag, 'value': elem.text})
                pl_tags.append(pl_tag)    
        return pl_tags

