"""
Controller for the SampleResource object.
Performs the operations to create, update and
delete such objects.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from sample_resource.models.SampleResource import SampleResource as SampleResourceModel
from sample_resource.utils.validators import validate_resource_name
import decimal, random

class SampleResource():
    """
    Manages creation/edition of SampleResources from the input of a given form.
    """
    
    @staticmethod
    def create(instance, aggregate_id, slice=None):
        try:
            if all(x in instance.__dict__ for x in ["name", "temperature_scale"]):
                sr = SampleResourceModel()
                sr.aggregate_id = aggregate_id
                sr.set_label(instance.__dict__['name'])
                sr.set_name(instance.__dict__['name'])
                if "temperature" in instance.__dict__:
                    # XML import (aggregate update)
                    sr.set_temperature(instance.__dict__['temperature'])
                else:
                    # Normal form
                    sr.set_temperature(decimal.Decimal(random.randrange(1000))/1000)
                sr.set_temperature_scale(instance.__dict__['temperature_scale'])
                if slice:
                    sr.set_project_id(slice.project.id)
                    sr.set_project_name(slice.project.name)
                    sr.set_slice_id(slice.id)
                    sr.set_slice_name(slice.name)
                sr.save()
        except Exception as e:
            if "Duplicate entry" in str(e):
                raise Exception("SampleResource with name '%s' already exists." % str(instance.name))
            else:
                raise e

    @staticmethod
    def fill(instance, slice, aggregate_id, resource_id = None):
        # resource_id = False => create. Check that no other resource exists with this name
        if not resource_id:
            if SampleResourceModel.objects.filter(name = instance.name):
                # Every exception will be risen to the upper level
                raise Exception("SampleResource with name '%s' already exists." % str(instance.name))

            instance.aggregate_id = aggregate_id
            instance.temperature = decimal.Decimal(random.randrange(1000))/100
            instance.project_id = slice.project.id
            instance.project_name = slice.project.name
            instance.slice_id = slice.id
            instance.slice_name = slice.name
        # resource_id = True => edit. Change name/label
        instance.label = instance.name
        return instance

    @staticmethod
    def delete(resource_id):
        try:
            SampleResourceModel.objects.get(id = resource_id).delete()
        except:
            pass

