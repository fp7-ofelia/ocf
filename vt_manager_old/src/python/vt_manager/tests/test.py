from vt_manager.communication.utils import *
xml = xmlFileToString('communication/prova.xml')
clase = parseXmlString(xml)
xml2 = craftXmlClass(clase)
clase2 = parseXmlString(xml2)

act = 0
print (clase.provisioning.action[act].id == clase2.provisioning.action[act].id )

for act in range(2):#clase.provisioning.action:
#    print act
    print (clase.provisioning.action[act].id == clase2.provisioning.action[act].id )
    #print (clase.provisioning.action[act].action_type == clase2.provisioning.action[act].action_type )
    print (clase.provisioning.action[act].virtual_machine.name == clase2.provisioning.action[act].virtual_machine.name )
    print (clase.provisioning.action[act].virtual_machine.uuid == clase2.provisioning.action[act].virtual_machine.uuid )
    print (clase.provisioning.action[act].virtual_machine.project_id == clase2.provisioning.action[act].virtual_machine.project_id )
    print (clase.provisioning.action[act].virtual_machine.slice_id == clase2.provisioning.action[act].virtual_machine.slice_id )
    print (clase.provisioning.action[act].virtual_machine.virtualization_type == clase2.provisioning.action[act].virtual_machine.virtualization_type )  
    print (clase.provisioning.action[act].virtual_machine.xen_configuration.hd_setup_type == clase2.provisioning.action[act].virtual_machine.xen_configuration.hd_setup_type )
