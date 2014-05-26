'''
Cleans inconsistent data from the database.
This is done in order to keep it coherent and thus not 
interfering with the manage.py commands, etc.

Created on Apr 10, 2014

@author: CarolinaFernandez
'''

from django.core.management.base import NoArgsCommand
from models import Action, VirtualMachine

class Command(NoArgsCommand):
    help = "Cleans inconsistent data from the database"

    def handle_noargs(self, **options):
        # Model 'action' from app 'models'
        # Remove actions whose foreign keys point to non-existent objects
        vms_uuid = [ x.uuid for x in VirtualMachine.objects.all()]
        inconsistent_actions = Action.objects.all().exclude(objectUUID__in = vms_uuid)
        length_inconsistent_actions = len(inconsistent_actions)
        inconsistent_actions.delete()
        #Action.objects.all().exclude(requestUser__in = User.objects.all())
        self.stdout.write("\n%s actions removed\n" % str(length_inconsistent_actions))
