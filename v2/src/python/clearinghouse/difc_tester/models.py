from clearinghouse.difc import models as difc_models
from django.db import models

class TestModel(difc_models.SecureModel):
    a = models.IntegerField()
    b = models.IntegerField()
    c = models.IntegerField()
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return u"%s" % self.name
    
class TestModel2(difc_models.SecureModel):
    d = models.IntegerField()
    other = models.ForeignKey(TestModel)
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return u"%s" % self.name
    
