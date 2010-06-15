from django import forms
from django.contrib.auth.models import User

class FVServerForm(forms.Form):
    name = forms.CharField(max_length = 40)
    url = forms.URLField()
    username = forms.CharField(max_length = 100)
    password = forms.CharField(label='password',
                            widget=forms.PasswordInput(render_value=False)) 
    max_password_age = forms.IntegerField(max_value = 3650)
    verify_certs = forms.BooleanField(required=False)
    
def pack_fvserver_info(fvserverp):
    result={}
    result["name"] = fvserverp.name
    result["username"] = fvserverp.username
    result["password"] = fvserverp.password
    result["url"] = fvserverp.url
    result["max_password_age"] = fvserverp.max_password_age
    result["verify_certs"] = fvserverp.verify_certs
    return result