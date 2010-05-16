'''
Created on May 15, 2010

@author: jnaous
'''
from django.db import models

class DummyFV(models.Model): pass

class DummyFVDevice(models.Model):
    dpid = models.CharField(max_length=23)
    fv = models.ForeignKey(DummyFV)

    def __str__(self):
        return self.dpid

class DummyFVLink(models.Model):
    src_dev = models.ForeignKey(DummyFVDevice)
    src_port = models.IntegerField()
    dst_dev = models.ForeignKey(DummyFVDevice)
    dst_port = models.IntegerField()
    fv = models.ForeignKey(DummyFV)
    
    def __str__(self):
        return "%s,%s,%s,%s" % (self.src_dev, self.src_port,
                                self.dst_dev, self.dst_port)

class DummyFVSlice(models.Model):
    name = models.CharField(max_length=500, unique=True)
    password = models.CharField(max_lengh=1024)
    controller_url = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    fv = models.ForeignKey(DummyFV)
    
class DummyFVRuleManager(models.Manager):
    """
    Store in decreasing order of priority.
    """
    def create(self, *args, **kwargs):
        rule = super(DummyFVRuleManager, self).create(*args, **kwargs)
        self.add(rule)
        return rule
        
    def add(self, rule):
        if self.count() == 0:
            rule.is_head = True
            rule.prev = rule
            rule.save()
            return rule.id
        else:
            from django.db.models import Q
            normal = Q(priority__le=rule.priority,
                       prev__priority__ge=rule.priority)
            end = Q(is_head=True,
                    prev__priority__ge=rule.priority)
            start = Q(is_head==True,
                      priority__le=rule.priority)
            before = self.filter(
                normal|end|start).select_related()[0]
            if before.is_head and before.priority <= rule.priority:
                rule.is_head = True
                before.is_head = False
            rule.prev = before.prev
            before.prev = rule
            before.save()
            rule.save()
    
class DummyFVRule(models.Model):
    
    objects = DummyFVRuleManager()
    
    fv = models.ForeignKey(DummyFV)

    match = models.CharField(max_length=2048)
    actions = models.CharField(max_length=200)
    prev = models.OneToOneField('self', related_name="next",
                                null=True, blank=True)
    is_head = models.BooleanField(default=False)
    priority = models.Integer()
    dpid = models.CharField(max_length=100)

    def _remove_from_list(self):
        if self.prev != self:
            self.next.prev = self.prev
            self.next.save()
        self.prev = self
        self.save()
        
    def change_priority(self, priority):
        """
        Use this function to change priority so we can put the rule
        in the right location.
        """
        self.priority = priority
        self._remove_from_list()
        self.objects.add(self)
        
    def delete(self):
        self._remove_from_list()
        return super(models.Model, self).delete()
    