from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from opts.models import Experiment, ExperimentFLowSpace

class Command(BaseCommand):
    args = "<slice_urn>"
    help = "Remove experiment and flowspaces associated to the given slice urn"

    def remove_experiment_and_fs(self, slice_urn):
        if slice_urn is None:
            return
        exps = Experiment.objects.filter(Q(project_name=slice_urn) | Q(slice_urn=slice_urn))
        for exp in exps:
            fs = ExperimentFLowSpace.objects.filter(exp=exp)
            fs.delete()
            if len(fs) == 0:
                exp.delete()
                self.stdout.write("Removing slice and flowspaces with exp_id='%s'\n" % slice_urn)

    def handle(self, *args, **options):
        self.remove_experiment_and_fs(args)
