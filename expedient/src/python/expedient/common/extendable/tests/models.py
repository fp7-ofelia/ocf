'''
@author: jnaous
'''
from django.db import models
from expedient.common.extendable.models import Extendable

class OtherModel(models.Model):
    pass

class OtherModelRel(models.Model):
    child = models.ForeignKey("TestChild")
    other = models.ForeignKey(OtherModel)

class YetAnotherModel(models.Model):
    pass

class YetAnotherModelRel(models.Model):
    child = models.ForeignKey("TestOtherChild")
    other = models.ForeignKey(YetAnotherModel)

class TestParent(Extendable):
    class Extend:
        fields = {
            'other': (models.ManyToManyField,
                      [None],
                      {'through': None},
                      ['other_model'],
                      {'through': 'other_through'},
                     ),
        }
        mandatory = [
            'other_model',
            'other_through',
        ]

class TestChild(TestParent):
    class Extend:
        replacements = {
            'other_model': OtherModel,
            'other_through': OtherModelRel,
        }

class TestOtherChild(TestParent):
    class Extend:
        replacements = {
            'other_model': YetAnotherModel,
            'other_through': YetAnotherModelRel,
        }
