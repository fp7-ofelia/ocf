'''
@author: jnaous
'''

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from clearinghouse import users
from clearinghouse.users import forms
from django.views.generic import create_update
from django.contrib import auth

def detail(request, proj_id):
    '''Show information about the project and functions'''
    