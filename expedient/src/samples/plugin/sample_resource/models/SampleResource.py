from django.db import models
from expedient.clearinghouse.resources.models import Resource
from sample_resource.utils.validators import TEMPERATURE_SCALE_CHOICES, validate_resource_name, validate_temperature_scale

class SampleResource(Resource):
    
    class Meta:
        """Meta class for SampleResource model."""
        app_label = 'sample_resource'

    # Unique alphanumeric identifier for the SampleResource
    label = models.CharField(max_length = 100, unique=True)
    temperature = models.DecimalField(max_digits = 6, decimal_places = 3, blank = True)
    temperature_scale = models.CharField(max_length = 10, verbose_name = "Temperature scale",
                        choices = TEMPERATURE_SCALE_CHOICES,
                        validators = [validate_temperature_scale])
    connections = models.ManyToManyField("SampleResource", blank = True, null = True)
#    connections = models.ManyToManyField("Resource", blank = True, null = True)
    project_id = models.CharField(max_length = 1024, default = "")
    project_name = models.CharField(max_length = 1024, default = "")
    slice_id = models.CharField(max_length = 1024, default = "")
    slice_name = models.CharField(max_length = 1024, default = "")

    def get_connections(self):
        return self.connections.all()

    def set_connections(self, connections):
        for connection in connections:
            self.connections.add(connection)

    def get_name(self):
        return self.name

    def set_name(self, name):
        # Adds or overwrites any validation to Resource's "name" field
        if not self.name:
            validate_resource_name(name)
            self.name = name

    def get_label(self):
        return self.label

    def set_label(self, label):
        if not self.label:
            validate_resource_name(label)
            self.label = label

    def get_temperature(self):
        return self.temperature

    def set_temperature(self, temperature):
        self.temperature = temperature

    def get_temperature_scale(self):
        return self.temperature_scale

    def set_temperature_scale(self, temperature_scale):
        self.temperature_scale = temperature_scale

    # Returns the whole string ("C" => "Celsius", "F" => "Fahrenheit", etc)
    def get_full_temperature_scale(self):
        try:
            return dict(TEMPERATURE_SCALE_CHOICES)[self.get_temperature_scale()]
        except:
            return self.get_temperature_scale()

    def get_project_id(self):
        return self.project_id

    def set_project_id(self, project_id):
        if not isinstance(project_id,str):
            project_id = str(project_id)
        self.project_id = project_id

    def get_project_name(self):
        return self.project_name

    def set_project_name(self,project_name):
        if not isinstance(project_name,str):
            project_name = str(project_name)
        self.project_name = project_name

    def get_slice_id(self):
        return self.slice_id

    def set_slice_id(self, value):
        self.slice_id = value

    def get_slice_name(self):
        return self.slice_name

    def set_slice_name(self, value):
        self.slice_name = value

    def delete(self):
        for connection in self.connections.all():
            self.connections.remove(connection)
#            connection.delete() # deletes connected resources as well
        super(SampleResource, self).delete()

