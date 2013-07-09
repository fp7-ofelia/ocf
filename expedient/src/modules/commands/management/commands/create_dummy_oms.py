'''Has command to create dummy Opt-in Managers for testing.
Created on Oct 5, 2010

@author: jnaous
'''
from django.core.management.base import NoArgsCommand
from optparse import make_option
from openflow.dummyom.models import DummyOM

class Command(NoArgsCommand):
    help = "Create dummy Opt-In Managers for testing."
    option_list = NoArgsCommand.option_list + (
        make_option(
            '--num', action='store', dest='num',
            default=3,
            help='Specifies the number of dummy OMs to create. Defaults to 3',
        ),
        make_option(
            '--num_links', action='store', dest='num_links',
            default=10,
            help='Specifies the number of dummy links to create. Defaults to 10',
        ),
        make_option(
            '--num_switches', action='store', dest='num_switches',
            default=5,
            help='Specifies the number of dummy switches to create. Defaults to 10',
        ),
    )

    def handle_noargs(self, **options):
        num_oms = options.get("num", 3)
        num_links = options.get("num_links", 10)
        num_switches = options.get("num_switches", 5)
        for i in xrange(num_oms):
            print "Creating DummyOM %s" % (i+1)
            om = DummyOM.objects.create()
            om.populate_links(num_switches=num_switches, num_links=num_links)
        print "Done."

