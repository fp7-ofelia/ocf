from threading import Thread
from django.contrib.sessions.models import Session
import datetime
from django.db import transaction

'''
        author:lbergesio, omoya
        Encapsulates the method used to clean up old expired sessions from the db      
'''

class SessionMonitoringThread(Thread):

    def __init__(self, method=None):
       Thread.__init__(self)
       self.__method = method

#    def __cleanUpExpiredSessions(self):
#        try:
#            # Recover expired sessions and delete them
#            expired_sessions = Session.objects.filter(expire_date__lt = datetime.datetime.now())
#            for expired_session in expired_sessions:
#                expired_session.delete()
#                transaction.commit_unless_managed()
#        except Exception as e:
#            print "Could not clean app db for expired sessions. Consider doing it manually.\nException was: %s\n" % str(e)

    @staticmethod
    def monitorSessionInNewThread():
        thread = SessionMonitoringThread(clean_up_expired_sessions)
        thread.startMethod()
        return thread

    def startMethod(self):
        self.start()

    def run(self):
        # XXX Disabled due to Out-of-Memory
        #self.__method()
        pass

def clean_up_expired_sessions():
    try:
        # Recover expired sessions and delete them
        expired_sessions = Session.objects.filter(expire_date__lt = datetime.datetime.now())
        for expired_session in expired_sessions:
            expired_session.delete()
            transaction.commit_unless_managed()
    except Exception as e:
        print "Could not clean app db for expired sessions. Consider doing it manually.\nException was: %s\n" % str(e)

