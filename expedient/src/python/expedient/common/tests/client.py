'''
Created on May 21, 2010

Contains functions to login and manage forms.

@author: jnaous
'''
import urllib, urllib2, cookielib
import logging
from pprint import pformat
logger = logging.getLogger("expedient.common.tests.client")

def fake_login(client, user):
    """Setup the client to appear logged in even if it isn't.
    
    @param client: The client to setup
    @type client: C{django.test.Client}
    @param user: The user to log the client in as.
    @type user: C{django.contrib.auth.models.User}
    """
     
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.http import HttpRequest
    from django.contrib.auth import login
    
    engine = import_module(settings.SESSION_ENGINE)

    # Create a fake request to store login details.
    request = HttpRequest()
    if client.session:
        request.session = client.session
    else:
        request.session = engine.SessionStore()
    login(request, user)

    # Save the session values.
    request.session.save()

    # Set the cookie to represent the session.
    session_cookie = settings.SESSION_COOKIE_NAME
    client.cookies[session_cookie] = request.session.session_key
    cookie_data = {
        'max-age': None,
        'path': '/',
        'domain': settings.SESSION_COOKIE_DOMAIN,
        'secure': settings.SESSION_COOKIE_SECURE or None,
        'expires': None,
    }
    client.cookies[session_cookie].update(cookie_data)    

def parse_form(doc):
    """
    parse the doc (a string), and return a dictionary of
    name->value.
    """
    from pyquery import PyQuery as pq
    
    d = pq(doc, parser="html")
    inputs = d("input")
    
    # filter the ones that have a name
    inputs = [i for i in inputs if i.name]
    
    return dict([(i.name, i.value) for i in inputs])

def test_get_and_post_form(
    client, url, params, del_params=[], post_url=None):
    """
    Get the form at C{url}, modify named parameters by those in C{params},
    then submit at C{post_url} or C{url} if C{post_url} is unspecified.
    Return response. This function uses the Django TestClient C{client}.
    
    @param client: client to use to make requests.
    @type client: Django C{TestClient}.
    @param url: URL to get the form from.
    @type url: string
    @param params: parameters to update the form with.
    @type params: dict
    @keyword del_params: list of parameter names to delete from form. These
        parameters are not submitted.
    @type del_params: list of strings
    @keyword post_url: (optional) URL to post the form to. If None then port to
        C{url} instead.
    @type post_url: str or None
    @return: response from client.post()
    @rtype: Test Response instance.
    """
    post_url = post_url or url
    resp = client.get(url)
    logger.debug("Response received using get: \n%s" % resp)
    if resp.status_code != 405 and resp.status_code != 302:
        form_params = parse_form(resp.content)
        logger.debug("Form params received: \n%s" % pformat(form_params))
        form_params.update(params)
    else:
        form_params = params
    for k in del_params:
        if k in form_params:
            del form_params[k]
    for k, v in form_params.items():
        if v == None:
            del form_params[k]
    resp = client.post(post_url, form_params)
    logger.debug("Posting back using params \n%s" % pformat(form_params))
    logger.debug("Response after post:\n%s" % resp)
    return resp

class Browser(object):
    
    def __init__(self):
        self.cookiejar = cookielib.CookieJar()
    
    def get_form_inputs(self, doc):
        return parse_form(doc) 
     
    def get_select_choices(self, doc, select_name):
        """
        parse the doc (a string), and return a dictionary of all
        options and their values
        """
        from pyquery import PyQuery as pq
        
        result={}
        
        d = pq(doc, parser="html")

        selects = d("select")

        for i in range(0,len(selects)):
            if selects.eq(i).attr.name == select_name:
                options = selects.find('option')
                for j in range(0,len(options)):
                    result[options.eq(j).text()] = options.eq(j).attr.value

        return result
    
    def get_checkbox_choices(self, doc):
        """
        parse the doc (a string), and return a dictionary of
        name->text. The checkboxes should be of the following format:
        <input type="checkbox" name="something">text</input>
        """
        from pyquery import PyQuery as pq
        
        d = pq(doc, parser="html")
        inputs = d("input")
        result = {}
        
        for i in range(0,len(inputs)):
            if inputs.eq(i).attr.type=="checkbox":
                choice = str(inputs.eq(i)).split(">")[1].lstrip()
                result[choice] = inputs.eq(i).attr.name
        
        return result
    
    def get_form(self,url):
        """
        Get the form at 'url'
        
        @param url: URL to get the form from.
        @type url: string

        @return: response from urllib2.urlopen
        @rtype: file-like object (see L{urllib2.urlopen})
        """
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        urllib2.install_opener(opener)
        f = urllib2.urlopen(url)
        return f
    
    def get_and_post_form(self, url, params, del_params=[], post_url=None):
        """
        Get the form at 'url', modify named parameters by those in 'params',
        then submit at 'post_url' or 'url' if 'post_url' is unspecified.
        Return response.
        
        @param url: URL to get the form from.
        @type url: string
        @param params: parameters to update the form with.
        @type params: dict
        @param post_url: (optional) URL to post the form to. If None then port to
            C{url} instead.
        @keyword del_params: list of parameter names to delete from form. These
            parameters are not submitted.
        @type del_params: C{list} of C{str}
        @type post_url: str or None
        @return: response from urllib2.urlopen
        @rtype: file-like object (see L{urllib2.urlopen})
        """
        
        post_url = post_url or url
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        urllib2.install_opener(opener)
        f = urllib2.urlopen(url)
        form_params = self.get_form_inputs(f.read())
        form_params.update(params)

        for k in del_params:
            if k in form_params:
                del form_params[k]
    
        data = urllib.urlencode(form_params)
        req = urllib2.Request(url=post_url, data=data)
        req.add_header('Referer', url)
        f = urllib2.urlopen(req)
        return f
    
    def login(self, url, username, password):
        """
        Log in at the given URL.
        
        @param url: url of the login page.
        @type url: str
        @param username: username to use for login.
        @type username: str
        @param password: password to use for login
        @type password: str
        @return: True on success, False otherwise.
        """
        
        try:
            f = self.get_and_post_form(
                url, dict(
                    username=username,
                    password=password,
                )
            )
        except Exception:
            return False
        
        if f.geturl() != url:
            # redirected (hopefully) to the success page
            return True
        else:
            return False
        
        