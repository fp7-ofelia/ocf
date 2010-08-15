'''
@author: jnaous
'''
from expedient.common.tests.manager import SettingsTestCase
from models import OtherModel, OtherModelRel, TestChild, TestOtherChild, \
    TestParent, YetAnotherModel

class Tests(SettingsTestCase):
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'expedient.common.extendable',
            'expedient.common.extendable.tests',
        ))
        self.settings_manager.set(DEBUG_PROPAGATE_EXCEPTIONS=True)
        self.parent = TestParent.objects.create()
        self.child1 = TestChild.objects.create()
        self.child2 = TestOtherChild.objects.create()
        self.other = OtherModel.objects.create()
        self.another = YetAnotherModel.objects.create()
        
    def test_as_leaf_class(self):
        """
        Test the as_leaf_class method.
        """
        
        parents = TestParent.objects.all()
        self.assertEqual(type(parents[0]), TestParent)
        self.assertEqual(type(parents[0].as_leaf_class()), TestParent)
        
        self.assertEqual(type(parents[1]), TestParent)
        self.assertEqual(type(parents[1].as_leaf_class()), TestChild)

        self.assertEqual(type(parents[2]), TestParent)
        self.assertEqual(type(parents[2].as_leaf_class()), TestOtherChild)

    def test_relations(self):
        """
        Make sure we can create relationships that are extended, and
        relationships with wrong types fail.
        """
        other_rel = OtherModelRel.objects.create(child=self.child1,
                                                 other=self.other)
        self.assertEqual(type(other_rel.child), TestChild)
        self.assertRaises(ValueError,
                          OtherModelRel.objects.create,
                          child=self.child2,
                          other=self.another)
        
        self.assertRaises(ValueError,
                          OtherModelRel.objects.create,
                          child=self.child1,
                          other=self.another)
