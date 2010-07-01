'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import OpenFlowAggregate, OpenFlowSliceInfo, OpenFlowConnection
from openflow.plugin.models import OpenFlowInterface
from expedient.common.utils import create_or_update

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
    
    connections = forms.ModelMultipleChoiceField(
        OpenFlowConnection.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Existing Connections")

    def __init__(self, queryset, *args, **kwargs):
        super(OpenFlowConnectionSelectionForm, self).__init__(*args, **kwargs)
        self.fields["connections"].queryset = queryset
    
class OpenFlowStaticConnectionForm(forms.Form):
    """
    A form for selecting a local and a remote interface to create a static
    bi-directional connection.
    """
    
    local_interface = forms.ModelChoiceField(
        OpenFlowInterface.objects.all())
    
    remote_interface = forms.ModelChoiceField(
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
    