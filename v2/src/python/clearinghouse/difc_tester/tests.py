'''
Created on Mar 11, 2010

@author: jnaous
'''

from django.db.models.query import QuerySet, Q
from django.test import TestCase
from clearinghouse.difc.models import *
from clearinghouse.difc.checks import can_flow
from clearinghouse.difc_tester.models import *
from django.contrib.auth.models import User

class TestAll(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owneruser', 'email@bla.com', 'password')
        self.user = User.objects.create_user('testuser', 'email@bla.com', 'password')
        threadlocals.push_current_user(self.owner)

        self.cat1 = Category.objects.create()
        self.cat2 = Category.objects.create()
        self.cat3 = Category.objects.create()
        
#        self.catset1 = CategorySet.objects.create()
#        self.catset1.categories.add(self.cat1)
#        self.catset2 = CategorySet.objects.create()
#        self.catset2.categories.add(self.cat2)
#        self.catset12 = CategorySet.objects.create()
#        self.catset12.categories.add(self.cat1)
#        self.catset12.categories.add(self.cat2)
#        self.catset13 = CategorySet.objects.create()
#        self.catset13.categories.add(self.cat1)
#        self.catset13.categories.add(self.cat3)
#        self.catset23 = CategorySet.objects.create()
#        self.catset23.categories.add(self.cat3)
#        self.catset23.categories.add(self.cat2)
#        self.catset123 = CategorySet.objects.create()
#        self.catset123.categories.add(self.cat1)
#        self.catset123.categories.add(self.cat2)
#        self.catset123.categories.add(self.cat3)

        self.m1 = TestModel.objects.create(a=1, b=1, c=1, name="m1")
        self.m2 = TestModel.objects.create(a=2, b=2, c=2, name="m2")
        self.m3 = TestModel.objects.create(a=3, b=3, c=1, name="m3")
        
        self.fm1 = TestModel2.objects.create(d=5, other=self.m1, name="fm1")
        self.fm2 = TestModel2.objects.create(d=10, other=self.m2, name="fm2")
        
        self.ffm1 =  TestModel3.objects.create(d=100, other=self.m1, name="ffm1")
        self.ffm1.m2m_mods.add(self.m1)
        self.ffm2 =  TestModel3.objects.create(d=100, other=self.m2, name="ffm2")
        self.ffm2.m2m_mods.add(self.m2)
        self.ffm3 =  TestModel3.objects.create(d=100, other=self.m3, name="ffm3")
        self.ffm3.m2m_mods.add(self.m3)
        self.ffm12 =  TestModel3.objects.create(d=100, other=self.m3, name="ffm12")
        self.ffm12.m2m_mods.add(self.m1, self.m2)
        self.ffm123 =  TestModel3.objects.create(d=100, other=self.m3, name="ffm123")
        self.ffm123.m2m_mods.add(self.m1, self.m2, self.m3)
        
    def tearDown(self):
        del threadlocals.get_current_label()[0][:]
        del threadlocals.get_current_label()[1][:]
        
        
    def test_can_flow(self):
        '''Tests that the can_flow function is correct.'''
#        self.m1.a_secrecy_label.add(self.catset1)
        self.m1.a_secrecy_label.add(self.cat1)
#        self.m2.a_secrecy_label.add(self.catset12)
        self.m2.a_secrecy_label.add(self.cat1)
        self.m2.a_secrecy_label.add(self.cat2)
        self.assertTrue(can_flow(self.m1.get_FIELD_label("a"),
                                 self.m2.get_FIELD_label("a")))
        self.assertFalse(can_flow(self.m2.get_FIELD_label("a"),
                                  self.m1.get_FIELD_label("a")))
        
#        self.m1.a_secrecy_label.add(self.catset12)
        self.m1.a_secrecy_label.add(self.cat2)
        self.assertTrue(can_flow(self.m1.get_FIELD_label("a"),
                                 self.m2.get_FIELD_label("a")))
        self.assertTrue(can_flow(self.m2.get_FIELD_label("a"),
                                 self.m1.get_FIELD_label("a")))
        
#        self.m1.a_integrity_label.add(self.catset13)
        self.m1.a_integrity_label.add(self.cat1, self.cat3)
        self.assertTrue(can_flow(self.m1.get_FIELD_label("a"),
                                 self.m2.get_FIELD_label("a")))
        self.assertFalse(can_flow(self.m2.get_FIELD_label("a"),
                                  self.m1.get_FIELD_label("a")))

        self.m2.a_integrity_label.add(self.cat1, self.cat2, self.cat3)
        self.assertFalse(can_flow(self.m1.get_FIELD_label("a"),
                                  self.m2.get_FIELD_label("a")))
        self.assertTrue(can_flow(self.m2.get_FIELD_label("a"),
                                 self.m1.get_FIELD_label("a")))
                    
    def test_allowed_mod(self):
        threadlocals.get_current_label()[0].extend([self.cat1])
        threadlocals.get_current_label()[1].extend([self.cat1, self.cat2])
        
        self.m1.a_secrecy_label.add(self.cat1, self.cat3)
        
        self.m1.a = 10
        self.m1.save()

    def test_disallowed_mod(self):
        threadlocals.get_current_label()[0].extend([self.cat1, self.cat3])
        threadlocals.get_current_label()[1].extend([self.cat1, self.cat2])
        
        self.m1.a = 10
        self.assertRaises(checks.SecurityException, self.m1.save)

        self.m1.a_secrecy_label.add(self.cat1, self.cat2, self.cat3)
        self.m1.save()
        
        self.m1.a_integrity_label.add(self.cat1, self.cat2, self.cat3)
        self.m1.a = 11
        self.assertRaises(checks.SecurityException, self.m1.save)
        
    def test_constrained_query(self):
        self.m1.a_secrecy_label.add(self.cat1, self.cat2)
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertFalse(self.m1 in qs)
        self.assertTrue(self.m2 in qs)
        self.assertTrue(self.m3 in qs)

        threadlocals.get_current_label()[0].extend([self.cat3])
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertFalse(self.m1 in qs)
        self.assertTrue(self.m2 in qs)
        self.assertTrue(self.m3 in qs)

        threadlocals.get_current_label()[0].extend([self.cat1, self.cat2])
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertTrue(self.m1 in qs)
        self.assertTrue(self.m2 in qs)
        self.assertTrue(self.m3 in qs)
        
        threadlocals.get_current_label()[1].extend([self.cat1])
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertFalse(self.m1 in qs)
        self.assertFalse(self.m2 in qs)
        self.assertFalse(self.m3 in qs)
        
        self.m1.a_integrity_label.add(self.cat1)
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertTrue(self.m1 in qs)
        self.assertFalse(self.m2 in qs)
        self.assertFalse(self.m3 in qs)

        self.m1.a_integrity_label.add(self.cat2)
        self.m2.a_integrity_label.add(self.cat2)
        qs = TestModel.objects.filter(a__in=[1,2,3])
        self.assertTrue(self.m1 in qs)
        self.assertFalse(self.m2 in qs)
        self.assertFalse(self.m3 in qs)
        
    def test_extended_constrained_query(self):
        self.fm1.other_secrecy_label.add(self.cat1)
        qs = TestModel2.objects.filter(other__in=[self.m1,self.m2, self.m3])
        self.assertFalse(self.fm1 in qs)
        self.assertTrue(self.fm2 in qs)

        threadlocals.get_current_label()[0].extend([self.cat1])
        qs = TestModel2.objects.filter(other__in=[self.m1,self.m2, self.m3])
        self.assertTrue(self.fm1 in qs)
        self.assertTrue(self.fm2 in qs)

        self.m1.a_secrecy_label.add(self.cat2)
        qs = TestModel2.objects.filter(other__a__in=[1,2,3])
        self.assertFalse(self.fm1 in qs)
        self.assertTrue(self.fm2 in qs)
        
        threadlocals.get_current_label()[0].extend([self.cat2])
        qs = TestModel2.objects.filter(other__in=[self.m1,self.m2, self.m3])
        self.assertTrue(self.fm1 in qs)
        self.assertTrue(self.fm2 in qs)

    def test_reverse_constrained_query(self):
        qs = TestModel.objects.filter(testmodel2__in=[self.fm1, self.fm2])
        self.assertTrue(self.m1 in qs)
        self.assertTrue(self.m2 in qs)

        self.fm1.d_secrecy_label.add(self.cat1)
        qs = TestModel.objects.filter(testmodel2__d__gt=0)
        print qs.query
        self.assertFalse(self.m1 in qs)
        self.assertTrue(self.m2 in qs)
        
    def test_m2m_constrained_query(self):
        self.ffm123.m2m_mods_secrecy_label.add(self.cat1)
        qs = TestModel3.objects.filter(m2m_mods=self.m1)
        self.assertTrue(self.ffm1 in qs)
        self.assertTrue(self.ffm12 in qs)
        self.assertFalse(self.ffm123 in qs)
        self.assertFalse(self.ffm2 in qs)
        self.assertFalse(self.ffm3 in qs)
        
        threadlocals.get_current_label()[0].extend([self.cat1])
        qs = TestModel3.objects.filter(m2m_mods=self.m1)
        self.assertTrue(self.ffm1 in qs)
        self.assertTrue(self.ffm12 in qs)
        self.assertTrue(self.ffm123 in qs)
        self.assertFalse(self.ffm2 in qs)
        self.assertFalse(self.ffm3 in qs)
        
        self.m1.a_secrecy_label.add(self.cat2)
        qs = TestModel3.objects.filter(m2m_mods__a__gt=0)
        self.assertFalse(self.ffm1 in qs)
        self.assertTrue(self.ffm12 in qs)
        self.assertTrue(self.ffm123 in qs)
        self.assertTrue(self.ffm2 in qs)
        self.assertTrue(self.ffm3 in qs)
        