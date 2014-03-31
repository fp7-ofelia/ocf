#!/usr/bin/python 
from lxml import etree
from StringIO import StringIO
from foam.sfa.util.xrn import Xrn, urn_to_hrn
from foam.sfa.rspecs.rspec import RSpec
from foam.sfa.rspecs.version_manager import VersionManager

xslt='''<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
'''

xslt_doc=etree.parse(StringIO(xslt))
transform=etree.XSLT(xslt_doc)

class PGRSpecConverter:

    @staticmethod
    def to_sfa_rspec(rspec, content_type = None):
        if not isinstance(rspec, RSpec):
            pg_rspec = RSpec(rspec)
        else:
            pg_rspec = rspec
        
        version_manager = VersionManager()
        sfa_version = version_manager._get_version('sfa', '1')    
        sfa_rspec = RSpec(version=sfa_version)

        #nodes = pg_rspec.version.get_nodes()
        #sfa_rspec.version.add_nodes(nodes())
        #sfa_rspec.version.add_links(pg_rspec.version.get_links())
        #return sfa_rspec.toxml() 

        # get network
        networks = pg_rspec.version.get_networks()
        network_hrn = networks[0]["name"]
        network_element = sfa_rspec.xml.add_element('network', name=network_hrn, id=network_hrn)
        
        # get nodes
        pg_nodes_elements = pg_rspec.version.get_nodes()
        nodes_with_slivers = pg_rspec.version.get_nodes_with_slivers()
        i = 1
        for pg_node in pg_nodes_elements:
            attribs = dict(pg_node.items())
            attribs['id'] = 'n'+str(i)
            
            node_element = network_element.add_element('node')
            for attrib in attribs:
                if type(attribs[attrib]) == str:
                    node_element.set(attrib, attribs[attrib])
            urn = pg_node["component_id"]
            if urn:
                if type(urn)==list:
                    # legacy code, not sure if urn is ever a list...
                    urn = urn[0]
                hostname = Xrn.urn_split(urn)[-1]
                hostname_element = node_element.add_element('hostname')
                hostname_element.set_text(hostname)
                if hostname in nodes_with_slivers:
                    node_element.add_element('sliver')

            for hardware_type in pg_node["hardware_types"]:
                if "name" in hardware_type:
                    node_element.add_element("hardware_type", name=hardware_type["name"])
                     
            # just copy over remaining child elements  
            #for child in pg_node_element.getchildren():
            #    node_element.append(transform(child).getroot())
            i = i+1
 
        return sfa_rspec.toxml()
         
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:        
        print PGRSpecConverter.to_sfa_rspec(sys.argv[1])  
