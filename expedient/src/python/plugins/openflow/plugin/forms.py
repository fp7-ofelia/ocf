'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from models import OpenFlowAggregate, OpenFlowSliceInfo, OpenFlowConnection
from openflow.plugin.models import OpenFlowInterface, NonOpenFlowConnection
from expedient.common.utils import create_or_update
from django.forms.models import ModelChoiceField
from expedient.clearinghouse.slice.models import Slice
from expedient.common.utils.plugins.plugincommunicator import PluginCommunicator

class OpenFlowAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = OpenFlowAggregate
        # "vlan_auto_assignment" and "flowspace_auto_approval" only available to set by its corresponding IM
        exclude = ['client', 'owner', 'users', "leaf_name", "vlan_auto_assignment", "flowspace_auto_approval"]

class OpenFlowSliceInfoForm(forms.ModelForm):
    class Meta:
        model = OpenFlowSliceInfo
        exclude = ["slice"]

#class OpenFlowSliceControllerForm(OpenFlowSliceInfoForm):
class OpenFlowSliceControllerForm(forms.ModelForm):
    class Meta:
        model = OpenFlowSliceInfo
        fields = ["controller_protocol", "slice_vms", "controller_ip", "controller_port"]

    class VMModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, vm):
            vm_server = vm.vtserver_set.all()[0].name
            vm_ip = vm.ifaces.all().exclude(ip__isnull=True)[0].ip
            return "%s (server: %s, ip: %s)" % (vm.name, vm_server, vm_ip)

    controller_protocol = forms.ChoiceField(
        choices=[("tcp","tcp"),("ssl","ssl")],
        required=True,
        initial="tcp",
        label="Protocol")

    slice_vms = VMModelChoiceField(
        queryset=[],
        # Disables first label entirely
#        empty_label=None,
#        widget=forms.Select,
        required=False,
        label="Controller IP (from current slice)")

    controller_ip = forms.CharField(
        required=False,
        label="Controller IP (from other slice)")
    
    controller_port = forms.IntegerField(
        required=True,
        label="Controller port")
    
    def __init__(self, *args, **kwargs):
        # XXX Critical: remove 'slice' from kwargs before calling parent constructor
        # Otherwise signature method will changeand problems will arise!
        self.slice = kwargs.pop('slice', None)
        super(OpenFlowSliceControllerForm, self).__init__(*args, **kwargs)
        slice_vms = None
        # Note: instance (or OpenFlowSliceInfo) is not initially filled.
        # When no controller has been set yet, the dropdown is empty...
        try:
            slice_vms = PluginCommunicator.get_objects(self.slice, "vt_plugin", "VM", sliceId=self.slice.uuid)
        except Exception as e:
            print "OpenFlow plug-in: cannot find list of VMs. Exception: %s" % str(e)
        
        # Fill with initial info
        try:
            controller_address = self.instance.__dict__["controller_url"].split(":")
            self.fields["controller_protocol"].initial = controller_address[0]
            self.fields["controller_ip"].initial = controller_address[1]
            try:
                # Obtain index for VM in dropdown list through the slice controller IP
                chosen_controller_pk = slice_vms.get(ifaces__ip=controller_address[1]).id
                self.fields["slice_vms"].initial = chosen_controller_pk
            except:
                pass
            self.fields["controller_port"].initial = controller_address[2]
        except:
            pass
        # Fill dropdown with data from the database. Call PluginCommunicator to get VMs
        if slice_vms:
            self.fields["slice_vms"].queryset = slice_vms
#            self.fields["controller_ip"].widget = forms.HiddenInput()
        # If there are no VMs in the slice, there is no need to show the dropdown
        else:
            self.fields["slice_vms"].widget = forms.HiddenInput()

    def controller_is_unique(self, controller_url):
        """
        Detect any other controller with the same address (protocol, ip, port)
        that may be present in a *started* slice.
        """
        # Exclude protocol from controller address
        try:
            controller_url = ":".join(controller_url.split(":")[1:])
        except:
            pass
        # Exclude current slice from the filter
        existing_controllers = OpenFlowSliceInfo.objects.exclude(slice=self.instance.slice_id)
        started_slices = Slice.objects.all().filter(started=True).exclude(id=self.instance.slice_id)
        started_slices_ids = [ slice.id for slice in started_slices ]

        # Filter controllers from started slices
        started_slice_controllers = map(lambda x: x.controller_url, filter(lambda x: x.slice_id in started_slices_ids, existing_controllers))
        # Remove protocol in controllers. This adds no value, we shall check for IP and port only
        started_slice_controllers = [ ":".join(con.split(":")[1:]) for con in started_slice_controllers ]
        return (controller_url not in started_slice_controllers)
    
    def clean(self):
        # Manual IP by default. Check later on if user chose from the dropdown list
        controller_ip = ""
        try:
            controller_ip = self.cleaned_data["controller_ip"]
        except Exception as e:
           print "OpenFlow plug-in: user-seletected IP could not be retrieved. Exception: %s" % str(e)

        if not controller_ip:
            try:
                # Obtain IP from VM selected in the dropdown
                controller_vm = PluginCommunicator.get_object(self.slice, "vt_plugin", "VM", pk=self.cleaned_data["slice_vms"])
                controller_ip = controller_vm.ifaces.all().exclude(ip__isnull=True)[0].ip
            except Exception as e:
                print "OpenFlow plug-in: cannot retrieve IP from selected VM. Exception: %s" % str(e)
                raise ValidationError(u"Could not obtain IP from controller.")
       
        if "controller_port" in self.cleaned_data and "controller_protocol" in self.cleaned_data and controller_ip:
            self.cleaned_data["controller_url"] = "%s:%s:%s" % (self.cleaned_data["controller_protocol"], controller_ip, self.cleaned_data["controller_port"])
            if not self.controller_is_unique(self.cleaned_data["controller_url"]):
                raise ValidationError(u"Controller '%s:%s' is already being used. Choose another." % (controller_ip, self.cleaned_data["controller_port"]))
            # Remove data that will not be saved into the model
            #keys_to_pop = filter((lambda key: key  != "controller_url"), self.cleaned_data.keys())
            #[ self.cleaned_data.pop(key) for key in keys_to_pop ]
            # XXX Important. Update controller_url field in the model, by changing the instance
            self.instance.controller_url = str(self.cleaned_data["controller_url"])
        else:
            raise ValidationError(u"Could not obtain a valid controller address. Ensure your input is correct.")
        return self.cleaned_data

    # Validation of the input fields
    def clean_controller_ip(self):
        controller_ip = None
        if "controller_ip" in self.cleaned_data:
            controller_ip = self.cleaned_data["controller_ip"]
        # Optional field. May not be there
        if controller_ip:
            validators.validate_ipv4_address(controller_ip)
        return controller_ip

    def clean_controller_port(self):
        min_port_permitted = 1
        max_port_permitted = 65535
        controller_port = None
        if "controller_port" in self.cleaned_data:
            controller_port = self.cleaned_data["controller_port"]
            if int(controller_port) >= max_port_permitted:
                raise ValidationError(u"Controller port is bigger than permitted (%s)" % max_port_permitted)
            elif int(controller_port) < 1:
                raise ValidationError(u"Controller port is lower than permitted (%s)" % min_port_permitted)
        # Required field. Must be there
        else:
            raise ValidationError(u"Introduce the controller port")
        return controller_port

class OpenFlowConnectionSelectionForm(forms.Form):
    """
    A form to select multiple openflow connections.
    """
    
    of_connections = forms.ModelMultipleChoiceField(
        OpenFlowConnection.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Existing OpenFlow Connections")

    non_of_connections = forms.ModelMultipleChoiceField(
        NonOpenFlowConnection.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Existing Non-OpenFlow Connections")

    def __init__(self, of_cnxn_qs, non_of_cnxn_qs, *args, **kwargs):
        super(OpenFlowConnectionSelectionForm, self).__init__(*args, **kwargs)
        self.fields["of_connections"].queryset = of_cnxn_qs
        self.fields["non_of_connections"].queryset = non_of_cnxn_qs
    
class AsLeafClassModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        if hasattr(obj, "as_leaf_class"):
            return "%s" % obj.as_leaf_class()
    
class OpenFlowStaticConnectionForm(forms.Form):
    """
    A form for selecting a local and a remote interface to create a static
    bi-directional connection.
    """
    
    local_interface = AsLeafClassModelChoiceField(
        OpenFlowInterface.objects.all())
    
    remote_interface = AsLeafClassModelChoiceField(
        OpenFlowInterface.objects.all())
    
    def __init__(self, aggregate, *args, **kwargs):
        super(OpenFlowStaticConnectionForm, self).__init__(*args, **kwargs)

        self.fields["local_interface"].queryset = \
            OpenFlowInterface.objects.filter(aggregate__id=aggregate.id)
    
        self.fields["remote_interface"].queryset = \
            OpenFlowInterface.objects.exclude(aggregate__id=aggregate.id)
        
    def save_connections(self):
        """
        Create two unique unidirectional links between the two interfaces.
        
        @return: tuple of the created connections. If a connection is not
            created, None is returned for it.
        """
        
        cnxn1, created = create_or_update(
            OpenFlowConnection,
            filter_attrs=dict(
                src_iface = self.cleaned_data["local_interface"],
                dst_iface = self.cleaned_data["remote_interface"],
            ),
        )
        if not created:
            cnxn1 = None
        
        cnxn2, created = create_or_update(
            OpenFlowConnection,
            filter_attrs=dict(
                dst_iface = self.cleaned_data["local_interface"],
                src_iface = self.cleaned_data["remote_interface"],
            ),
        )
        if not created:
            cnxn2 = None
        
        return (cnxn1, cnxn2)

class NonOpenFlowStaticConnectionForm(forms.ModelForm):
    """
    A form for selecting a local interface and a non-openflow resource to
    create a static connection.
    """
    
    class Meta:
        model = NonOpenFlowConnection
        
    def __init__(self, aggregate, resource_qs, *args, **kwargs):
        super(NonOpenFlowStaticConnectionForm, self).__init__(*args, **kwargs)

        self.fields["of_iface"].queryset = \
            OpenFlowInterface.objects.filter(aggregate__id=aggregate.id)
    
        self.fields["resource"].queryset = resource_qs

