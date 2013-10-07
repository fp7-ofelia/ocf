#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
"""
Model for the Bowl aggregate.
It defines the fields that will be used in the CRUD form.

@date: Jul 8, 2013
@author: Theresa Enghardt
"""

from django import forms
from bowl_plugin.models import BowlResourceAggregate as BowlResourceAggregateModel

class BowlResourceAggregate(forms.ModelForm):
    '''
    A form to create and edit BowlResource Aggregates.
    '''

    #sync_resources = forms.BooleanField(label = "Sync resources?", initial = True, required = False)

    class Meta:
        model = BowlResourceAggregateModel
        exclude = ['client', 'owner', 'users', 'available']

