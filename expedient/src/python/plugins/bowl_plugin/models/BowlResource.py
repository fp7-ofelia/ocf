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
from django.db import models
from expedient.clearinghouse.resources.models import Resource

class BowlResource(Resource):
    
    class Meta:
        """Meta class for BowlResource model."""
        app_label = 'bowl_plugin'

    # Unique alphanumeric identifier for the BowlResource
    label = models.CharField(max_length = 100, unique=True)
    connections = models.ManyToManyField("BowlResource", blank = True, null = True)
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
        super(BowlResource, self).delete()

