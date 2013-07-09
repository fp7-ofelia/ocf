'''Defines models for the timer app.
Created on Feb 16, 2011

@author: jnaous
'''

import sys
from django.db import models
from utils import stringify_func
from datetime import datetime, timedelta
from expedient.common.timer.exceptions import JobAlreadyScheduled,\
    JobNotScheduled
from django.core.urlresolvers import get_callable
from django.db.models.signals import post_syncdb

class JobManager(models.Manager):
    def schedule_post_syncdb(self, period, callable_func):
        """Schedule a new periodic job after syncdb is done.
        
        You will need to use this function for scheduling if
        you are getting errors saying that the time_job table
        does not exist in the database.
        
        See L{JobManager.schedule}.
        
        """
        from expedient.common.timer import models as timer_app

        uid = "schedule_post_syncdb_job_%s_%s" % (period, callable_func.__name__)

        def schedule_callback_factory():
            def schedule_callback(sender, **kwargs):
                try:
                    self.schedule(period, callable_func)
                except JobAlreadyScheduled:
                    pass
            return schedule_callback

        post_syncdb.connect(
            schedule_callback_factory(),
            sender=timer_app,
            weak=False,
            dispatch_uid=uid,
        )
    
    def schedule(self, period, callable_func):
        """Schedule a new periodic job.
        
        New job will call C{callable} every C{period} seconds. If 
        C{callable} is already registered with another job,
        this function will raise an JobAlreadyScheduled exception.
        
        This method cannot be used to schedule jobs before syncdb
        has been done (i.e. for example outside a function context).
        For that you need to use C{Job.objects.schedule_post_syncdb}.
        See L{JobManager.schedule_post_syncdb}.
        
        @param period: time between runs in seconds.
        @type period: integer
        @param callable: function to call for executing the job.
        @type callable: Callable
        @return: The new L{Job} instance.
        @raise JobAlreadyScheduled: If callable is already
            called by another Job.
            
        """
        callable_name = stringify_func(callable_func)
        next_run_time = datetime.now() + timedelta(seconds=period)
        job, created = self.get_or_create(
            callable_name=callable_name,
            defaults=dict(
                period=period,
                next_run_time=next_run_time,
            )
        )
        if not created:
            raise JobAlreadyScheduled(job)
        else:
            return job
        
    def unschedule(self, callable_func):
        """Removes periodic scheduling of a job.
        
        @param callable: The callable which was used to
            schedule the job.
        @type callable: Callable.
        @raise JobNotScheduled: If callable is not scheduled.
        
        """
        try:
            job = self.get(
                callable_name=stringify_func(callable_func))
        except self.model.DoesNotExist:
            raise JobNotScheduled(callable_func)
        job.delete()
        
    def get_for(self, callable_func):
        """Get the job corresponding the callable."""
        return self.get(
            callable_name=stringify_func(callable_func))

class Job(models.Model):
    """Describes a periodic job."""
    
    next_run_time = models.DateTimeField(
        help_text="When the next job is scheduled.")
    period = models.BigIntegerField(
        help_text="Time between job runs in seconds.")
    callable_name = models.CharField(
        help_text="Name of function to call.", unique=True,
        max_length=255)
    
    objects = JobManager()    

    def reset_timer(self):
        self.next_run_time = datetime.now() \
            + timedelta(seconds=self.period)
        self.save()
        
    def execute_now(self):
        """Executes this job right away."""
        callable_func = get_callable(self.callable_name)
        return callable_func()
        
    def conditional_execute(self):
        """Executes this job if the timer has passed and resets it."""
        
        if self.next_run_time <= datetime.now():
            r = self.execute_now()
            self.reset_timer()
            return (r, True)

        else:
            return (None, False)

    def __unicode__(self):
        return u"Job calls %s every %s seconds" % (
            self.callable_name, self.period)
