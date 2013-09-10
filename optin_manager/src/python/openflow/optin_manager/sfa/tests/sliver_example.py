rspec = '''<rspec  xmlns="http://www.geni.net/resources/rspec/3" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:openflow="http://www.geni.net/resources/rspec/ext/openflow/3" xs:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/ext/openflow/3 http://www.geni.net/resources/rspec/ext/openflow/3/of-resv.xsd" type="request">
   <openflow:sliver email="a@b.com" description="OF request example">
      <openflow:controller url="tcp:192.168.1.1" type="primary"/>
       <openflow:group name="fs1">
          <openflow:datapath component_id="urn:publicid:IDN+openflow:optin:i2cat.of_ocf+datapath:06:a4:00:12:e2:b8:a5:d0" 
                             component_manager_id="urn:publicid:IDN+openflow:optin:i2cat.of_optin+authority+am" 
                             dpid="06:a4:00:12:e2:b8:a5:d0">
             <openflow:port name="ETH0" num="0"/>
             <openflow:port name="ETH1" num="1"/>
          </openflow:datapath>
          <openflow:datapath component_id="urn:publicid:IDN+openflow:optin:i2cat.of_ocf+datapath:06:af:00:24:a8:c4:b9:00" 
                             component_manager_id="urn:publicid:IDN+openflow:optin:i2cat.of_optin+authority+am"
                             dpid="06:af:00:24:a8:c4:b9:00">
             <openflow:port name="ETH3" num="3"/>
             <openflow:port name="ETH4" num="4"/>
          </openflow:datapath>
       </openflow:group>
       <openflow:match>
          <openflow:use-group name="fs1" />
          <openflow:packet>
             <openflow:dl_type value="0x800" />
             <openflow:nw_src value="10.1.1.0/24" />
             <openflow:nw_proto value="6, 17" />
             <openflow:tp_src value="80" />
          </openflow:packet>
       </openflow:match>
       <openflow:match>
          <openflow:use-group name="fs1" />
          <openflow:packet>
              <openflow:dl_type value="0x800" />
	      <openflow:dl_vlan value= "2"/>
              <openflow:nw_dst value="10.1.1.0/24" />
              <openflow:nw_proto value="6, 17" />
              <openflow:tp_dst value="80" />
          </openflow:packet>
          </openflow:match>
   </openflow:sliver>
</rspec>'''	
