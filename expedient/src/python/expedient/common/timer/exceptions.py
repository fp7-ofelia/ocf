'''Contains exceptions for the timer app.
Created on Feb 16, 2011

@author: jnaous
'''
from expedient.common.timer.utils import stringify_func

class TimerException(Exception):
    pass

class JobAlreadyScheduled(TimerException):
    """Raised when a job is scheduled twice.
    
    @ivar conflicting_job: the job that already exists.
    @type conflicting_job: L{expedient.common.timer.models.Job}
    """
    
    def __init__(self, conflicting_job):
        super(JobAlreadyScheduled, self).__init__(
            "Conflicting job found: '%s'" % conflicting_job,
        )
        self.conflicting_job = conflicting_job

class JobNotScheduled(TimerException):
    """Raised when a callable is not scheduled in a job.
    
    @ivar callable: the callable that raised the error
    @type callable: Callable.
    """
    
    def __init__(self, callable_func):
        super(JobNotScheduled, self).__init__(
            "Job for callable '%s' not found." % stringify_func(callable_func),
        )
        self.callable_func = callable_func
