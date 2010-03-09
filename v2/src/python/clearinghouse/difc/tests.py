"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from clearinghouse.difc.models import *

class SimpleTest(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create()
        self.cat2 = Category.objects.create()

        self.m1 = SecureModel.objects.create(a=1, b=1, c=1)
        self.m2 = SecureModel.objects.create(a=2, b=2, c=2)
        self.m3 = SecureModel.objects.create(a=3, b=3, c=1)
        
        self.m1.a_label.add(self.cat1)
        self.m2.a_label.add(self.cat1)
        self.m2.a_label.add(self.cat2)

    def test_simple(self):
        q = SecureModel.objects.only("a", "b") #.filter(c=1)
        for o in q:
            print o
        print list(q)
        
