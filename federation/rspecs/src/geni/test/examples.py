RAW_NODES = '''<node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="0"
                  component_id="urn:publicID:ThisisaURNof0"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="1"
                  component_id="urn:publicID:ThisisaURNof1"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="2"
                  component_id="urn:publicID:ThisisaURNof2"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="3"
                  component_id="urn:publicID:ThisisaURNof3"
                  exclusive="true">
                  <available now="none"/>
                  </node>'''
                  
AD_RSPEC = '''<?xml version="1.0" encoding="UTF-8"?>
                    <rspec xmlns="http://www.geni.net/resources/rspec/3"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd"
                    type="advertisement">
<node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="0"
                  component_id="urn:publicID:ThisisaURNof0"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="1"
                  component_id="urn:publicID:ThisisaURNof1"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="2"
                  component_id="urn:publicID:ThisisaURNof2"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="3"
                  component_id="urn:publicID:ThisisaURNof3"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               </rspec>'''
               
RAW_MANIFEST = '''   <node client_id="None"
                        component_id="None"
                        component_manager_id="urn:publicID:ComponentManagerID120"
                        sliver_id="urn:publicID:Sliver0"/>
                     <node client_id="None"
                        component_id="None"
                        component_manager_id="urn:publicID:ComponentManagerID120"
                        sliver_id="urn:publicID:Sliver0"/>
                    <node client_id="None"
                        component_id="None"
                        component_manager_id="urn:publicID:ComponentManagerID120"
                        sliver_id="urn:publicID:Sliver0"/>'''
                        
FULL_MANIFEST = ''' <?xml version="1.0" encoding="UTF-8"?>
                    <rspec xmlns="http://www.geni.net/resources/rspec/3"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd"
                    type="manifest">
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
</rspec>'''

REQUEST_EXAMPLE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rspec generated="2014-03-22T01:53:21.460+01:00" generated_by="Experimental jFed Rspec Editor" type="request" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd" xmlns="http://www.geni.net/resources/rspec/3" xmlns:jFed="http://jfed.iminds.be/rspec/ext/jfed/1" xmlns:jFedBonfire="http://jfed.iminds.be/rspec/ext/jfed-bonfire/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:emulab="http://www.protogeni.net/resources/rspec/ext/emulab/1">
  <node client_id="node0" component_id="urn:publicid:IDN+wall2.ilabt.iminds.be+node+n095-01a" component_manager_id="urn:publicid:IDN+wall2.ilabt.iminds.be+authority+cm" exclusive="true">
      <sliver_type name="emulab-xen">
        <emulab:xen cores="10" ram="8192" disk="50"/>
        <disk_image name="urn:publicid:IDN+wall2.ilabt.iminds.be+image+emulab-ops//DEB60_64-VLAN"/>
     </sliver_type>
  </node>
</rspec>'''