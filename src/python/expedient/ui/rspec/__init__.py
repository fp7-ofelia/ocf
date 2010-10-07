from django.core.urlresolvers import reverse

def plugin(slice):
    return (
        "RSpec Manager",
        "Manage OpenFlow resources through RSpecs.",
        reverse("rspec_plugin_home", args=[slice.id])
    )
