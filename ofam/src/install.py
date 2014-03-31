#!/usr/bin/env python
# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import sys
import os
import shutil
from optparse import OptionParser
import subprocess

def output (data):
  if data.strip():
    print data

def call (cmd, show_cmd = True, show_output = True):
  if show_cmd:
    print cmd
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  (sout, serr) = p.communicate()
  if show_output:
    output(sout)
    output(serr)
  return sout

def symlink (src, dst):
  print "Creating symlink to %s from %s" % (src, dst)
  try:
    os.symlink(src, dst)
  except OSError, e:
    "Already exists!"

def copyfile (src, dst):
  print "Copying %s to %s" % (src, dst)
  shutil.copyfile(src, dst)

def fixup_version (opts):
  #rev = call('hg id -i').strip()
  #branch = call('hg id -b').strip()
  rev = 'to_be_tagged'
  branch = call('echo $(git branch | grep "*" | sed "s/* //")').strip()

  f = open("setup.py", "r")
  new_setup = []
  for line in f.readlines():
    if line.count("version"):
      new_setup.append("      version='%s (%s)',\n" % (rev, branch))
    else:
      new_setup.append(line)
  f.close()
  f = open("setup.py", "w+")
  f.write("".join(new_setup))

  f = open("src/foam/version.py", "w+")
  f.write("VERSION = '%s-%s'\n" % (rev, branch))
  f.close()

def addDir (path, owner):
  try:
    print "Making Directory: %s" % (path)
    os.makedirs(path)
  except OSError, e:
    pass
  call('chown %s %s' % (owner, path))

def install_foam ():
  call("python setup.py install")

  addDir("/opt/ofelia/ofam/local/db", "www-data")
  addDir("/opt/ofelia/ofam/local/etc/", "www-data")
  addDir("/opt/ofelia/ofam/local/etc/gcf-ca-certs", "root")
  addDir("/opt/ofelia/ofam/local/log", "www-data")
  addDir("/opt/ofelia/ofam/local/log/tasks", "www-data")
  addDir("/opt/ofelia/ofam/local/tasks/queue", "www-data")
  addDir("/opt/ofelia/ofam/local/tasks/completed", "www-data")
  addDir("/opt/ofelia/ofam/local/etc/templates/custom", "root")

def install_deps ():
  #res = call("pip --version")
  #ver = res.split()[1]
  #if ver != "1.0.2":
  #  call("pip install -U pip")
  call("apt-get --yes install python-pip nginx xmlsec1 python-dateutil m2crypto python-dev ssl-cert libxml2-dev libxslt1-dev libssl-dev swig")
  #res = call("pip --version")
  #ver = res.split()[1]
  #if ver != "1.0.2":
  call("pip install -U pip")
  # Initial arrangements in order to be able to install packages
  #call("pip -q install setuptools --no-use-wheel --upgrade")
  call("pip -q install ElementTree --allow-unverified ElementTree --allow-external ElementTree")
  pip_dependencies = ["python-dateutil", "M2Crypto", "SQLAlchemy", "Flask", "Flask-XML-RPC", "flup", "blinker", "lxml", "pyOpenSSL"]
  for dependency in pip_dependencies:
    call("pip -q install %s" % str(dependency))

def postinst (opts):
  call("/usr/sbin/make-ssl-cert generate-default-snakeoil")
  symlink("/etc/nginx/sites-available/foam.conf", "/etc/nginx/sites-enabled/foam.conf")
  copyfile("%s/debian/init.d" % (os.getcwd()), "/etc/init.d/foam")
  #making /etc/init.d/foam executable  
  call("chmod +x /etc/init.d/foam", False, False)
  # Maybe ask if you really want to revert setup.py right now?
  #call("hg revert setup.py src/foam/version.py --no-backup")
  call("git checkout setup.py", False, False) #revert all changes to setup (to be used later...)

def parse_args (argv):
  parser = OptionParser()
  #parser.add_option("--allow-uncommitted", dest="allow_uncommitted", default=False, action="store_true")
  parser.add_option("--allow-uncommitted", dest="allow_uncommitted", default=True, action="store_true")
  (opts, args) = parser.parse_args()
  return opts

def save_backup():
  print "Saving backup (db, unallowed vlans, certs)"
  call("service foam stop")
  call("service nginx stop")
  addDir("/opt/ofelia/ofam/backup/db", "www-data")
  addDir("/opt/ofelia/ofam/backup/etc", "www-data")
  addDir("/opt/ofelia/ofam/backup/etc/gcf-ca-certs", "root")
  addDir("/opt/ofelia/ofam/backup/etc/templates/custom", "root")
  addDir("/opt/ofelia/ofam/backup/other", "www-data")
  call("cp -r /opt/ofelia/ofam/local/db /opt/ofelia/ofam/backup")
  call("cp -r /opt/ofelia/ofam/local/etc /opt/ofelia/ofam/backup")
  call("cp /opt/ofelia/ofam/local/lib/foam/ofeliasettings/localsettings.py /opt/ofelia/ofam/backup/other/")
  #call("cp /opt/ofelia/ofam/local/lib/foam/ofeliasettings/vlanset.py /opt/ofelia/ofam/backup/other/")
  call("rm -r /opt/ofelia/ofam/local")
  print "Backup saved in backup folder and local installation cleared"

def load_backup():
  print "Loading backup (db, unallowed vlans)"
  call("rm -r /opt/ofelia/ofam/local/db")
  call("rm -r /opt/ofelia/ofam/local/etc")
  call("mv /opt/ofelia/ofam/backup/db /opt/ofelia/ofam/local")
  call("chown -R www-data /opt/ofelia/ofam/local/db")
  call("chgrp -R www-data /opt/ofelia/ofam/local/db")
  #call("chown www-data /opt/ofelia/ofam/local/db/*")
  call("mv /opt/ofelia/ofam/backup/etc /opt/ofelia/ofam/local")
  call("chown -R www-data /opt/ofelia/ofam/local/etc")
  call("chgrp -R www-data /opt/ofelia/ofam/local/etc")
  #call("chown www-data /opt/ofelia/ofam/local/etc/*")
  call("chown -R root /opt/ofelia/ofam/local/etc/gcf-ca-certs")
  call("chgrp -R root /opt/ofelia/ofam/local/etc/gcf-ca-certs")
  #call("chown root /opt/ofelia/ofam/local/etc/gcf-ca-certs/*")
  call("chown -R root /opt/ofelia/ofam/local/etc/templates/custom")
  call("chgrp -R root /opt/ofelia/ofam/local/etc/templates/custom")
  #call("chown root /opt/ofelia/ofam/local/etc/templates/custom/*")
  call("mv /opt/ofelia/ofam/backup/other/localsettings.py /opt/ofelia/ofam/local/lib/foam/ofeliasettings/localsettings.py")
  call("chown www-data /opt/ofelia/ofam/local/lib/foam/ofeliasettings/localsettings.py")
  call("chgrp www-data /opt/ofelia/ofam/local/lib/foam/ofeliasettings/localsettings.py")
  #call("mv /opt/ofelia/ofam/backup/other/vlanset.py /opt/ofelia/ofam/local/lib/foam/ofeliasettings/vlanset.py")
  #call("chown www-data /opt/ofelia/ofam/local/lib/foam/ofeliasettings/vlanset.py")
  #call("chgrp www-data /opt/ofelia/ofam/local/lib/foam/ofeliasettings/vlanset.py")
  call("rm -r /opt/ofelia/ofam/backup")
  call("foamctl admin:bundle-certs")
  call("service nginx restart")
  call("service foam restart")
  print "Backup loaded from backup folder, backup folder cleared and local installation is good to go"

def main ():
  if os.getuid() != 0:
    print "You must be root to run this installer."
    sys.exit(1)

  opts = parse_args(sys.argv)
  if not opts.allow_uncommitted:
    if call("git status", False, False).strip():
      print "You must commit all changes before running this installer."
      sys.exit(1)
  need_to_backup = False
  if (os.path.exists('/opt/ofelia/ofam/local')):
    need_to_backup = True
    print "Local installation already exists, need to handle backup"

  #fixup_version(opts) #deactivated for now (not crucial)
  if need_to_backup:
    save_backup()
  install_foam()
  install_deps()
  postinst(opts)
  if need_to_backup:
    load_backup()

if __name__ == '__main__':
  main()
