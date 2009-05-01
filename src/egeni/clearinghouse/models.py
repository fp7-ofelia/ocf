from django.db import models

class AggregateManager(models.Model):
    name = models.TextField(max_length=200)
    url = models.URLField('Aggregate Manager URL')
    key_file = models.TextField(max_length=200)
    cert_file = models.TextField(max_length=200)

    def __unicode__(self):
        return 'AM ' + self.name + ' at ' + self.url

