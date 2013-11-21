import sys
import time
import datetime

from foam.config import LOGDIR

def tracer (frame, event, arg):
  timestr = datetime.datetime.now().strftime("%H:%M:%S.%f")
  if (event == "call"):
    print "[%s] CALL: %s <%s>" % (timestr, frame.f_code.co_name, frame.f_code.co_filename)
  elif (event == "line"):
    print "[%s] LINE: %d (%s)" % (timestr, frame.f_lineno, frame.f_code.co_name)
  elif (event == "return"):
    print "[%s] RETURN: %s" % (timestr, frame.f_code.co_name)
  sys.stdout.flush()
  sys.stderr.flush()
  return tracer

def tracer_c (frame, event, arg):
  timestr = datetime.datetime.now().strftime("%H:%M:%S.%f")
  if (event == "c_call"):
    print "[%s] C CALL: %s" % (timestr, repr(arg))
  elif (event == "c_return"):
    print "[%s] C RETURN: %s" % (timestr, repr(arg))
  sys.stdout.flush()
  sys.stderr.flush()

class _Tracer(object):
  def __init__ (self):
    self.cur_fobj = None
    self.cur_fpath = None

  def enable (self):
    sys.settrace(None)
    sys.setprofile(None)

    self.cur_fpath = "%s/trace.%f.log" % (LOGDIR, time.time())
    self.cur_fobj = open(self.cur_fpath, "w")

    sys.stdout = self.cur_fobj
    sys.stderr = self.cur_fobj

    sys.settrace(tracer)
    sys.setprofile(tracer_c)

  def disable (self):
    sys.settrace(None)
    sys.setprofile(None)

    path = self.cur_fpath

    self.cur_fobj.flush()
    self.cur_fobj.close()
    self.cur_fobj = None
    self.cur_fpath = None

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    return path


Tracer = _Tracer()
