rspec ='''
<rspec xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="advertisement" xsi:schemaLocation="http://www.protogeni.net/resources/rspec/2 /opt/ofelia/vt_manager/src/python/vt_manager/communication/sfa/tests/vm_schema.xsd" expires="2013-02-18T12:15:30Z" generated="2013-02-18T11:15:30Z">
   <network name="vt_ocf" slice="">	
	<node component_manager_id="ocf.i2cat.vtmanager:c9883c61-16df-49cc-a8ea-8768d9b517a4authority+cm" component_id="58f565eb-b289-48aa-b4ac-61bc27cf1dea" exclusive="false" component_name="c9883c61-16df-49cc-a8ea-8768d9b517a4">
		<sliver>
			<name>mySFAVM2</name>
			<uuid>myuuid</uuid>
			<project-id>project1</project-id> 
			<slice-id>slice1</slice-id>
			<slice-name>SFATest</slice-name> 
			<operating-system-type>GNU/Linux</operating-system-type>
			<operating-system-version>5.0</operating-system-version>
			<operating-system-distribution>Debian</operating-system-distribution>
			<server-id>serverid</server-id>
			<hd-setup-type>file-image</hd-setup-type> 
			<hd-origin-path>default/test/lenny</hd-origin-path> 
			<virtualization-setup-type>paravirtualization</virtualization-setup-type> 
			<memory-mb>128</memory-mb>
			<interfaces>
				<interface ismgmt="true">
					<name>eth0</name>
					<mac>00:16:3E:2D:AE:27</mac>
					<ip>192.168.0.1</ip>
					<mask>255.255.255.0</mask>
					<gw>192.168.0.100</gw>
					<dns1>195.235.113.3</dns1>
					<dns2>80.58.0.33</dns2>
				</interface>
			</interfaces>
		</sliver>
	</node>
     </network>
</rspec>'''
#rspec = '''
'''
	<node>
		<slivers>
			<sliver>
                        <name>myName</name>
                        <uuid>myuuid</uuid>
                        <project-id>project1</project-id> 
                        <slice-id>slice1</slice-id> 
                        <operating-system-type>GNU/Linux</operating-system-type>
                        <operating-system-version>5.0</operating-system-version>
                        <operating-system-distribution>Debian</operating-system-distribution>
                        <server-id>serverid</server-id>
                        <hd-setup-type>file-image</hd-setup-type> 
                        <hd-origin-path>default/test/lenny</hd-origin-path> 
                        <virtualization-setup-type>paravirtualization</virtualization-setup-type> 
                        <memory-mb>512</memory-mb>
                        <interfaces>
                                <interface ismgmt="true">
                                        <name>eth0</name>
                                        <mac>00:16:3E:2D:AE:27</mac>
                                        <ip>192.168.0.1</ip>
                                        <mask>255.255.255.0</mask>
                                        <gw>192.168.0.100</gw>
                                        <dns1>195.235.113.3</dns1>
                                        <dns2>80.58.0.33</dns2>
                                </interface>
                                <interface>
                                        <name>eth1</name>
                                </interface>
                        </interfaces>
			</sliver>
                </slivers>
	</node>
'''	
