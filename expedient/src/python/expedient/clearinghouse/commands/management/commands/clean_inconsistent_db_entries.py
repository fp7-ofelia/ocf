'''
Cleans inconsistent data from the database.
This is done in order to keep it coherent and thus not 
interfering with the manage.py commands, etc.

Created on Apr 9, 2014

@author: CarolinaFernandez
'''

from django.core.management.base import NoArgsCommand
from vt_plugin.models import Action, VM
#from django.contrib.auth.models import User

class Command(NoArgsCommand):
    help = "Cleans inconsistent data from the database"

    def handle_noargs(self, **options):
        # Model 'actions' from app 'vt_plugin'
        # Remove actions whose foreign keys point to non-existent objects
        inconsistent_actions = Action.objects.all().exclude(vm__in = VM.objects.all())
        length_inconsistent_actions = len(inconsistent_actions)
        inconsistent_actions.delete()
        #Action.objects.all().exclude(requestUser__in = User.objects.all())
        self.stdout.write("\n%s actions removed\n" % str(length_inconsistent_actions))
