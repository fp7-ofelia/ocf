from threading import Thread
from django.contrib.sessions.models import Session
import datetime
from django.db import transaction

'''
        author:lbergesio
        Encapsulates the method used to clean up old expired sessions from the db      
'''

class SessionMonitoringThread(Thread):

    __method = None

    '''
    Description
    '''


    def __cleanUpExpiredSessions(self):
        try:
            #Recover expired sessions and delete them
            print Session.objects.filter(expire_date__lt=datetime.datetime.now())
            Session.objects.filter(expire_date__lt=datetime.datetime.now()).delete()
            transaction.commit_unless_managed()
        except Exception as e:
            print "Could not clean app db for expired sessions. Consider do it manually.\nException was: \n"+str(e)

    @staticmethod
    def monitorSessionInNewThread():
        thread = SessionMonitoringThread()
        thread.startMethod()
        return thread

    def startMethod(self):
        self.__method = self.__cleanUpExpiredSessions
        self.start()

    def run(self):
        self.__method()
