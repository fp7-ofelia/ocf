'''
Created on Feb 16, 2011

@author: jnaous
'''
from django.test import TestCase
from datetime import datetime
from expedient.common.timer.models import Job
from time import sleep
from expedient.common.timer.exceptions import JobAlreadyScheduled,\
    JobNotScheduled
from django.core.management import call_command
import logging
from django.db.models.signals import post_syncdb
from expedient.common.timer import models as timer_app

logger = logging.getLogger("timer.tests")

times = dict(
    job1_time=None,
    job2_time=None,
    job3_time=None,
    job4_time=None,
    job5_time=None,
    job6_time=None,
)

def jobx_call(i):
    times["job%s_time" % i] = datetime.now()
    logger.debug("Timer %s called." % i)

def job1_call():
    jobx_call(1)
def job2_call():
    jobx_call(2)
def job3_call():
    jobx_call(3)
def job4_call():
    jobx_call(4)
def job5_call():
    jobx_call(5)
def job6_call():
    jobx_call(6)

Job.objects.schedule_post_syncdb(4, job5_call)
Job.objects.schedule_post_syncdb(4, job6_call)

class Tests(TestCase):
    
    def test_methods(self):
        Job.objects.exclude(
            callable_name__regex=r'expedient.common.timer.tests.job.?_call$',
        ).delete()
        # create jobs
        Job.objects.schedule(4, job1_call)
        Job.objects.schedule(4, job2_call)
        Job.objects.schedule(4, job3_call)
        Job.objects.schedule(4, job4_call)
        
        # check that there are 6 jobs now including
        # the post syncdb one.
        self.assertEqual(
            Job.objects.count(), 6,
            "Wrong number of jobs. "
            "Existing job callables: %s" % 
            Job.objects.values_list("callable_name", flat=True),
        )
        
        # try to schedule an already scheduled job
        self.assertRaises(JobAlreadyScheduled, Job.objects.schedule, 1, job1_call)
        
        # wait 2s, delete one of the jobs that are supposed to run
        sleep(2)
        
        Job.objects.unschedule(job4_call)
        
        # check that there are 5 jobs now
        self.assertEqual(Job.objects.count(), 5)
        
        # try to unschedule a non-existent job
        self.assertRaises(JobNotScheduled, Job.objects.unschedule, job4_call)
        
        # check that conditional execution of a job not on
        # time won't do anything
        job1 = Job.objects.get_for(job1_call)
        ret = job1.conditional_execute()
        self.assertEqual(ret, (None, False))
        self.assertEqual(times["job1_time"], None)
        
        # reset the timer for job 3 so it executes 2 seconds after job1
        job3 = Job.objects.get_for(job3_call)
        job3.reset_timer()
        
        # check that jobs 1, 2, and 5 get executed on time
        # using the command
        self.assertEqual(times["job1_time"], None)
        self.assertEqual(times["job2_time"], None)
        self.assertEqual(times["job5_time"], None)
        self.assertEqual(times["job6_time"], None)
        sleep(2)
        self.assertEqual(times["job1_time"], None)
        self.assertEqual(times["job2_time"], None)
        self.assertEqual(times["job5_time"], None)
        self.assertEqual(times["job6_time"], None)
        call_command("run_timer_jobs")
        self.assertNotEqual(times["job1_time"], None)
        self.assertNotEqual(times["job2_time"], None)
        self.assertNotEqual(times["job5_time"], None)
        self.assertEqual(times["job3_time"], None)
        self.assertEqual(times["job4_time"], None)

        job1_time1 = times["job1_time"]
        job2_time1 = times["job2_time"]
        job5_time1 = times["job5_time"]
        
        # Check that the job was rescheduled
        job1 = Job.objects.get_for(job1_call)
        self.assertTrue(job1.next_run_time > datetime.now())
        
        # Check that conditional_execute works on job 3
        sleep(2)
        ret = job3.conditional_execute()
        self.assertTrue(ret[1])
        self.assertNotEqual(times["job3_time"], None)
        
        # check that jobs 1 and 2 run again after their period but not before
        job1 = Job.objects.get_for(job1_call)
        ret = job1.conditional_execute()
        self.assertEqual(ret, (None, False))
        self.assertEqual(times["job1_time"], job1_time1)
        
        sleep(2)
        call_command("run_timer_jobs")
        job1_time2 = times["job1_time"]
        job2_time2 = times["job2_time"]
        job5_time2 = times["job2_time"]

        self.assertTrue(job1_time2 > job1_time1)
        self.assertTrue(job2_time2 > job2_time1)
        self.assertTrue(job5_time2 > job5_time1)
        
        
