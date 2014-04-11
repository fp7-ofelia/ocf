'''
Cleans inconsistent data from the database.
This is done in order to keep it coherent and thus not 
interfering with the manage.py commands, etc.

Created on Apr 11, 2014

@author: CarolinaFernandez
'''

from django.core.management.base import NoArgsCommand
# django.contrib.auth.models.User needed for the following classes
from django.contrib.auth.models import User
from openflow.optin_manager.opts.models import Experiment
from openflow.optin_manager.opts.models import ExperimentFLowSpace
from openflow.optin_manager.opts.models import UserOpts
from openflow.optin_manager.opts.models import OptsFlowSpace
from openflow.optin_manager.opts.models import MatchStruct

class Command(NoArgsCommand):
    help = "Cleans inconsistent data from the database"

    def handle_noargs(self, **options):
        # Several models from app 'opts'
        # Remove experiment-related data whose foreign keys point to non-existent experiments
        inconsistent_experiment_flowspaces = ExperimentFLowSpace.objects.all().exclude(exp__in=Experiment.objects.all())
        self.stdout.write("\n%s experiment flowspaces removed\n" % str(len(inconsistent_experiment_flowspaces)))
        inconsistent_experiment_flowspaces.delete()
        inconsistent_user_opts = UserOpts.objects.all().exclude(experiment__in=Experiment.objects.all())
        self.stdout.write("\n%s user options removed\n" % str(len(inconsistent_user_opts)))
        inconsistent_user_opts.delete()
        inconsistent_flowspace_opts = OptsFlowSpace.objects.all().exclude(opt__in=UserOpts.objects.all())
        self.stdout.write("\n%s flowspace options removed\n" % str(len(inconsistent_flowspace_opts)))
        inconsistent_flowspace_opts.delete()
        inconsistent_match_structs = MatchStruct.objects.all().exclude(optfs__in=OptsFlowSpace.objects.all())
        self.stdout.write("\n%s match structures removed\n" % str(len(inconsistent_match_structs)))
        inconsistent_match_structs.delete()
