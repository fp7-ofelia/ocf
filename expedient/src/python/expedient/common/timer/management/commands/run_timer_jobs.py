'''Command to run the timer jobs that are due.
Created on Feb 16, 2011

@author: jnaous
'''

from django.core.management.base import NoArgsCommand
from expedient.common.timer.models import Job
from datetime import datetime

class Command(NoArgsCommand):
    help = "This command runs the jobs that are" \
        " scheduled using the expedient.common.timer app."

    def handle_noargs(self, **options):
        now = datetime.now()
        jobs = Job.objects.filter(next_run_time__lte=now)
        for j in jobs:
            j.execute_now()
            j.reset_timer()
            
