'''
Created on Jun 7, 2010

@author: jnaous
'''
from expedient.common.permissions.utils import register_class_default_permissions
from models import Resource, Sliver, SliverSet

register_class_default_permissions(Resource)
register_class_default_permissions(Sliver)
register_class_default_permissions(SliverSet)
