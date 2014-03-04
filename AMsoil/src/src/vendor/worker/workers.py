from datetime import datetime, timedelta
import time
import pickle

from amsoil.core import pluginmanager as pm
from amsoil.core import serviceinterface
from amsoil.core.exception import CoreException
import amsoil.core.log
logger=amsoil.core.log.getLogger('worker')

import workerdb

class WorkerServer(object):
    SLEEP_BETWEEN_CHECKS = 1 # sec
    
    def __init__(self):
        super(WorkerServer, self).__init__()

    @serviceinterface
    def runServer(self):
        """Runs the server which checks the database for new jobs regularly. This method blocks further execution (infinte loop)."""
        while True:
            records = workerdb.getAllJobs()
            for record in records:
                if record.next_execution == None or datetime.now() >= record.next_execution :
                    self._execute_job(record)
                    if record.recurring_interval: # change the next_execution if recurring, otherwise remove the job
                        record.next_execution=datetime.now() + timedelta(0, record.recurring_interval)
                        workerdb.commit()
                    else:
                        workerdb.delJob(record)
                        
            time.sleep(self.SLEEP_BETWEEN_CHECKS) # sec

    def _execute_job(self, record):
        # test if the job function has the required characteristics (can not be done while adding the job, because the service may not be loaded then)
        service = pm.getService(record.service_name)
        resolved_attr = getattr(service, record.callable_attr_str)
        if not hasattr(resolved_attr, '__call__'):
            logger.error("The attr given as job is not callable (%s, %s)" % (record.service_name, record.callable_attr))
            return
        if not hasattr(resolved_attr, '_outsideprocess'):
            logger.error("The attr given as job does not have the @outsideprocess attribute (%s, %s)" % (record.service_name, record.callable_attr))
            return
        # actually process the job
        try:
            params =  record.params
            resolved_attr(params)
        except Exception as e:
            logger.error("Job terminated with exception: %s" % (e,))

# --- client methods
@serviceinterface
def outsideprocess(func):
    """Annotation to mark a job function. Only functions marked with this annotation are accepted as jobs."""
    func._outsideprocess = True
    return func
    
def _addJob(service_name, callable_attr_str, params_for_pickle, recurring_interval=None, next_execution=None):
    """
    Actually adds the job to the queue and saves the job description to the database.
    
    There are four ways to call this function (recurring_interval, next_excution):
    - (None, None)    : A job which shall be executed as soon as possible
    - (None, datetime): A scheduled job which is executed around the datetime given
    - (60sec, None)    : A job to execute every 60 seconds, the first call is as soon as possible
    - (60sec, datetime): A job to execute every 60 seconds, but not before the given datetime
    """
    if recurring_interval: # check if there is not already an entry like this which is recurring
        records = workerdb.getAllJobs()
        for record in records:
            if record.service_name == service_name and record.callable_attr_str == callable_attr_str and record.recurring_interval:
                logger.info("Removing older recurring job with the same signature (%s, %s)" % (record.service_name, record.callable_attr_str))
                workerdb.delJob(record)
    entry = workerdb.JobDBEntry(service_name=service_name, callable_attr_str=callable_attr_str, params=params_for_pickle, recurring_interval=recurring_interval, next_execution=next_execution)
    workerdb.addJob(entry)

@serviceinterface
def add(service_name, callable_attr_str, params_for_pickle):
    """
    Adds a job to the queue, so the job will be executed as soon as possible.
    {params_for_pickle} are the parameters given to the {callable_attr} when the job gets executed.
    {params_for_pickle} should be serializable with pickle (hence, can be None).
    """
    _addJob(service_name, callable_attr_str, params_for_pickle, None, None)

@serviceinterface
def addAsScheduled(service_name, callable_attr_str, params_for_pickle, date_time):
    """
    Adds a job to the queue, so the job will be executed soon after the given {time} has passed.
    {params_for_pickle} are the parameters given to the {callable_attr} when the job gets executed.
    {params_for_pickle} should be serializable with pickle (hence, can be None).
    """
    _addJob(service_name, callable_attr_str, params_for_pickle, None, date_time)
    return None

@serviceinterface
def addAsReccurring(service_name, callable_attr_str, params_for_pickle, interval):
    """
    Adds a job to the queue, so the job will be executed roughly every {interval}.
    {interval} is specified in seconds.
    {params_for_pickle} are the parameters given to the {callable_attr} when the job gets executed.
    {params_for_pickle} should be serializable with pickle (hence, can be None).
    This method ensures that recurring tasks are added only once.
    """
    _addJob(service_name, callable_attr_str, params_for_pickle, interval, None)

