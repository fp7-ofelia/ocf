from django.db import models
from django.contrib import auth

class Slot(models.Model):
    """Slot"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    #def unicode__(self):
    #    return "%s:%s" % (self.projectID, self.__AMid)
   

 
    projectID = models.CharField(max_length = 1024, default="")       #Name of the project
    amID = models.CharField(max_length = 1024, default="")            #Name of the AM
    sliceID = models.CharField(max_length = 1024, default="")         #Name of the Slice
    slotID = models.IntegerField()                                    #Number of the slot (to make the difference with the id added by db), 
                                                                            #to be passed to binary
    AMslotID = models.IntegerField()                                  #Number of the AM part of the Slot to be passed to binary
    
    def setProjectID(self, value):
        self.projectID = value
    
    def setAMid(self, value):
        self.amID = value

    def setSliceID(self, value):
        self.sliceID = value

    def setSlotID(self, value):
        self.slotID = value

    def setAMslotID(self, value):
        self.AMslotID = value

    def getProjectID(self):
        return self.projectID

    def getAMid(self):
        return self.amID

    def getSliceID(self):
        return self.sliceID

    def getSlotID(self):
        return self.slotID

    def getAMslotID(self):
        return self.AMslotID

