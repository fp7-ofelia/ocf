from django.test import TestCase
from models import *

class SimpleTest(TestCase):
    pass

__test__ = {"doctest": """
Test the functionality of the extendable app

>>> from extendable_tester.models import *
>>> from django.contrib.contenttypes.models import ContentType
>>> parent = TestParent.objects.create()
>>> child1 = TestChild.objects.create()
>>> child2 = TestOtherChild.objects.create()
>>> other = OtherModel.objects.create()
>>> another = YetAnotherModel.objects.create()
>>> TestParent.objects.all()
[<TestParent: TestParent object>, <TestParent: TestParent object>, <TestParent: TestParent object>]
>>> [p.as_leaf_class() for p in TestParent.objects.all()]
[<TestParent: TestParent object>, <TestChild: TestChild object>, <TestOtherChild: TestOtherChild object>]
>>> [p.as_leaf_class() for p in TestParent.objects.all()]
[<TestParent: TestParent object>, <TestChild: TestChild object>, <TestOtherChild: TestOtherChild object>]
>>> other_rel = OtherModelRel(child=child1, other=other)
>>> other_rel.child
<TestChild: TestChild object>
>>> q = TestParent.objects.filter(content_type=ContentType.objects.get_for_model(TestChild))
>>> [p.as_leaf_class() for p in q]
[<TestChild: TestChild object>]
"""}
