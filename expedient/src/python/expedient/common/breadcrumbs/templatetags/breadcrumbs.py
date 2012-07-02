'''
Created on Jun 19, 2010

@author: jnaous
'''
from django import template

register = template.Library()

def get_links(trail):
    ret = ""
    for name, url in trail:
        if ret: ret += ' &gt; '
        ret += '<a href="%s">%s</a>' % (url, name)
    return ret

class BreadcrumbsNode(template.Node):
    def render(self, context):
        """
        If "breadcrumbs" is in the context, use that as the trail
        and store in session. If it is not, then use the trail from
        the session.
        """
        session = context["request"].session
        if "breadcrumbs" in context:
            trail = context["breadcrumbs"]
            session["breadcrumbs"] = trail
        else:
            trail = session.setdefault("breadcrumbs", [])
            context["breadcrumbs"] = trail
        return get_links(trail)
    
@register.tag
def breadcrumbs(parser, token):
    try:
        tag_name, = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag takes no arguments" % token.contents.split()[0]
    return BreadcrumbsNode()

@register.simple_tag
def last_link(trail):
    try:
        return trail[-1][1]
    except IndexError:
        return "/"

@register.simple_tag
def before_last_link(trail):
    try:
        return trail[-2][1]
    except IndexError:
        return "/"
