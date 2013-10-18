#!/usr/bin/env python

# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import sys
sys.path.append("/opt/ofelia/ofam/lib")

import subprocess
import json
import uuid
import urllib
import urllib2
import time
import os.path
import shutil
import smtplib
import email
import email.parser
import pprint
import traceback
from optparse import OptionParser

from foam.config import TASKLOGDIR, TASK_QUEUE_DIR, TASK_COMPLETED_DIR, TEMPLATE_DIR, USER_TEMPLATE_DIR
import foam.version
from foam.core.configdb import ConfigDB

URL = "https://localhost:3626/auto/%s"
LOC = os.path.dirname(os.path.realpath(__file__))
CMD = "%s/task.py" % (LOC)

def generateJobID ():
  return "%s" % (uuid.uuid4())

class Job(object):
  def __init__ (self, typ, jobdata):
    self.jobtype = typ
    self.jobid = generateJobID()
    d = {"__jobtype" : typ, "__data" : jobdata }

    path = "%s/%s.job" % (TASK_QUEUE_DIR, self.jobid)
    f = open(path, "w+")
    json.dump(d, f)
    f.close()

  def execute (self):
    p = subprocess.Popen("python %s %s -j %s" % (CMD, self.jobtype, self.jobid), shell=True)
    print "EXECUTE [%s]: %s" % (self.jobtype, self.jobid)
    return p.pid

def getEventTemplateData (event):
  if os.path.exists("%s/%s.txt" % (USER_TEMPLATE_DIR, event)):
    return open("%s/%s.txt" % (USER_TEMPLATE_DIR, event), "r").read()
  else:
    return open("%s/%s.txt" % (TEMPLATE_DIR, event), "r").read()

def sendEmail (event, tmpl_data, email_info, to_addr):
  data = {"event" : event, "template_data" : tmpl_data, "email_info" : email_info, "rcpt_list" : to_addr}
  job = Job("send-email", data)
  return job.execute()

def getExperimenterEmail (data):
  if data.has_key("email"):
    return data["email"]
  else:
    return None

def dispatchEmail (event, data):
  dispatch_admin = False
  dispatch_exp = False
  exp_email = None

  try:
    exp_email = getExperimenterEmail(data)
    dispatch_exp = ConfigDB.getConfigItemByKey("email.event.%s.exp" % (event)).getValue()
  except Exception, e:
    print traceback.format_exc()
    
  admin_email = ConfigDB.getConfigItemByKey("email.admin-addr").getValue()
  dispatch_admin = ConfigDB.getConfigItemByKey("email.event.%s.admin" % (event)).getValue()

  # Preserving for compatibility
  email_info = {"reply-to" : ConfigDB.getConfigItemByKey("email.reply-to").getValue(),
                "from" : ConfigDB.getConfigItemByKey("email.from").getValue(),
                "smtp_server" : ConfigDB.getConfigItemByKey("email.smtp-server").getValue()}

  data["admin_email"] = admin_email
  data["site"] = ConfigDB.getConfigItemByKey("geni.site-tag").getValue()

  if dispatch_admin:
    sendEmail("email.event.%s.admin" % (event), data, email_info, admin_email)
  if dispatch_exp and exp_email:
    sendEmail("email.event.%s.exp" % (event), data, email_info, exp_email)
  
# ====================
# == Task Launchers ==
# ====================
def approveSliver (sliver_urn, priority):
  data = {"sliver_urn" : sliver_urn, "priority" : priority}
  job = Job("approve-sliver", data)
  return job.execute()

def emailCreateSliver (sliver_data):
  dispatchEmail("createsliver", sliver_data)

def emailGAPIDeleteSliver (sliver_data):
  dispatchEmail("gapi-deletesliver", sliver_data)

def emailJSONDeleteSliver (sliver_data):
  dispatchEmail("json-deletesliver", sliver_data)

def emailApproveSliver (sliver_data):
  dispatchEmail("approvesliver", sliver_data)

def emailRenewSliver (sliver_data):
  dispatchEmail("renewsliver", sliver_data)

def emailRejectSliver (sliver_data):
  dispatchEmail("rejectsliver", sliver_data)

def emailDisableSliver (sliver_data):
  dispatchEmail("disablesliver", sliver_data)

def emailExpireSliver (sliver_data):
  dispatchEmail("expiresliver", sliver_data)

def emailSliverExpWeek (sliver_data):
  dispatchEmail("expiresliverweek", sliver_data)

def emailSliverExpDay (sliver_data):
  dispatchEmail("expiresliverday", sliver_data)

def emailPendingQueue (data):
  dispatchEmail("pendingqueue", data)

# ======================
# == ACTUAL TASK CODE ==
# ======================
def taskApproveSliver (opts):
  time.sleep(3)
  url = URL % ("approve-sliver")
  data = {"sliver_urn" : opts["sliver_urn"], "priority" : opts["priority"]}
  d = json.dumps(data)
  h = {"Content-Type" : "application/json"}
  req = urllib2.Request(url, d, h)
  response = urllib2.urlopen(req)
  pprint.pprint(response.read())

def taskExpireSlivers (opts):
  url = URL % ("expire-slivers")
  req = urllib2.Request(url)
  response = urllib2.urlopen(req)
  pprint.pprint(response.read())

def taskEmailSlivers (opts):
  url = URL % ("expire-emails")
  req = urllib2.Request(url)
  response = urllib2.urlopen(req)
  pprint.pprint(response.read())

def taskSendEmail (opts):
  s = smtplib.SMTP(opts["email_info"]["smtp_server"])
  tmplbuf = getEventTemplateData(opts["event"])
  tmpl = tmplbuf % (opts["template_data"])
  if isinstance(tmpl, unicode):
    tmpl = tmpl.encode('ascii')
  msg = email.message_from_string(tmpl)
  msg["To"] = opts["rcpt_list"]
  msg["From"] = opts["email_info"]["from"]
  rplyto = opts["email_info"]["reply-to"]
  if rplyto:
    msg["Reply-To"] = rplyto
  print opts
  print msg._headers
  s.sendmail(msg["From"], msg["To"], msg.as_string())
  s.quit()

def taskDailyQueue (opts):
  url = URL % ("email-queue")
  req = urllib2.Request(url)
  response = urllib2.urlopen(req)
  printJSONRPC(response.read())

# ===============
# == UTILITIES ==
# ===============

def printJSONRPC (data):
  rpc = json.loads(data)
  retcode = rpc["retcode"]
  if retcode == 0:
    print "SUCCESS"
    if rpc["msg"] != "":
      print rpc["msg"]
    if rpc["value"]:
      print rpc["value"]
  elif retcode == 1:
    print "JSON Parse Error"
    print rpc["msg"]
  elif retcode == 2:
    print "EXCEPTION"
    print rpc["msg"]

def nullParseArgs (args):
  return {}

def jobParseArgs (args):
  parser = OptionParser()
  parser.add_option("-j", dest="jobid", type="str")
  (opts, args) = parser.parse_args(args)

  opts = parseTaskFile(opts.jobid)
  return opts

def parseTaskFile (jobid, jobdata = True):
  print "JOB: %s" % jobid
  path = "%s/%s.job" % (TASK_QUEUE_DIR, jobid)
  f = open(path, "r")
  data = json.load(f)
  if jobdata:
    jdata = data["__data"]
    jdata["__jobid"] = jobid
    return jdata
  else:
    data["__jobid"] = jobid
    return data

def cleanup (opts):
  try:
    jobid = opts["__jobid"]
    path = "%s/%s.job" % (TASK_QUEUE_DIR, jobid)
    shutil.move(path, TASK_COMPLETED_DIR)
  except KeyError:
    pass
  except AttributeError:
    # non-job opts don't have __getitem__
    pass


CMDS = {'approve-sliver' : (taskApproveSliver, jobParseArgs),
        'expire-slivers' : (taskExpireSlivers, nullParseArgs),
        'email-slivers'  : (taskEmailSlivers, nullParseArgs),
        'send-email'     : (taskSendEmail, jobParseArgs),
        'daily-queue'    : (taskDailyQueue, nullParseArgs)}

# =====================
# == Parent Launcher ==
# =====================
if __name__ == '__main__':
  task_name = sys.argv[1]

  lpath = "%s/%s-%f.log" % (TASKLOGDIR, task_name, time.time())
  lfile = open(lpath, "w+")
  lfile.write("------------------------------\n")
  lfile.write("Version: %s\n" % (foam.version.VERSION))
  lfile.write("------------------------------\n")
  sys.stderr = lfile
  sys.stdout = lfile

  (task_func, parse_args) = CMDS[sys.argv[1]]
  opts = parse_args(sys.argv[2:])
  try:
    task_func(opts)
    cleanup(opts)
  except Exception, e:
    print traceback.format_exc()

  lfile.close()
