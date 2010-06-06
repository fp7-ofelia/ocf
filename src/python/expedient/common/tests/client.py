'''
Created on May 21, 2010

Contains functions to login and manage forms.

@author: jnaous
'''
import urllib, urllib2, cookielib

    
class browser():  
    
    def cookie_setup(self):
        """"
        call at the beginning to set up cookiejar
        """
        self.cookiejar = cookielib.CookieJar()        
        
    def get_form_params(self, doc):
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
        
    def get_and_post_form(self,url, params, post_url=None):
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
        @type post_url: str or None
        @return: response from urllib2.urlopen
        @rtype: file-like object (see L{urllib2.urlopen})
        """
        
        post_url = post_url or url
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        urllib2.install_opener(opener)
        f = urllib2.urlopen(url)
        form_params = self.get_form_params(f.read())
        form_params.update(params)
    
        data = urllib.urlencode(form_params)
        req = urllib2.Request(url=post_url, data=data)
        req.add_header('Referer', url)
        f = urllib2.urlopen(req)
        return f
    
    def login(self,url, username, password):
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
        
        