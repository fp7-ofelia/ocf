'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import OpenFlowAggregate, OpenFlowSliceInfo, OpenFlowConnection
from openflow.plugin.models import OpenFlowInterface, NonOpenFlowConnection
from expedient.common.utils import create_or_update
from django.forms.models import ModelChoiceField

class OpenFlowAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = OpenFlowAggregate
        exclude = ['client', 'owner', 'users']

class OpenFlowSliceInfoForm(forms.ModelForm):
    class Meta:
        model = OpenFlowSliceInfo
        exclude = ["slice"]

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
        if not created: cnxn1 = None
        
        cnxn2, created = create_or_update(
            OpenFlowConnection,
            filter_attrs=dict(
                dst_iface = self.cleaned_data["local_interface"],
                src_iface = self.cleaned_data["remote_interface"],
            ),
        )
        if not created: cnxn2 = None
        
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

