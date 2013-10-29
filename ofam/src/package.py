#!/usr/bin/env python
# Copyright (c) 2011-2012  The Board of Trustees of The Leland Stanford Junior University

import os
import os.path
from optparse import OptionParser
import shutil
import subprocess

VALID_DEB_DIALECTS = set([
  "lucid",
  "squeeze"
])

def package_rpm (opts):
  print "This package script does not currently support generating RPMs."

def setup_deb_dialect(dialect):
  if dialect not in VALID_DEB_DIALECTS:
    print "Unknown debian dialect: %s" % (dialect)
    sys.exit(1)

  # Right now the only thing we do with dialect setup is copy the proper
  # dialect control files (deps, post-install instructions, etc.)
  control_dir = "%s/debian/" % (os.getcwd())
  for f in os.listdir(control_dir):
    if os.path.isfile("%s/%s" % (control_dir, f)):
      if f.endswith(dialect):
        shutil.copyfile("%s/%s" % (control_dir, f),
                        "%s/%s" % (control_dir, f[:-(len(dialect)+1)]))

def getDialectRepoPath (dialect):
  return dialect

def package_deb (opts):
  setup_deb_dialect(opts.dialect)
  repo = getDialectRepoPath(opts.dialect)

  try:
    i = int(opts.tag)
    rc = False
  except ValueError:
    rc = True

  minor = opts.version.split(".")[1]
  if (int(minor) % 2):
    rtypes = ["unstable"]
  else:
    if not rc:
      rtypes = ["stable", "staging"]
    else:
      rtypes = ["staging"]

  debchange(opts.version, opts.tag)
  if rc:
    fixup_setup(opts.version, opts.tag)
  else:
    fixup_setup(opts.version)

  if opts.tag == "1":
    repo_tag(opts.version)
  build_deb(opts.version, opts.tag, rtypes, repo)

  print "----------------------------------------"
  if not rc:
    print "Make sure to HG COMMIT after this build!"
  else:
    call("hg revert --all --no-backup")
  
  drops = {}
  for rtype in rtypes:
    pkg = "/tmp/%s/%s/all/foam_%s-%s_all.deb" % (repo, rtype, opts.version, opts.tag)
    meta = "/tmp/%s/%s/Packages.gz" % (repo, rtype)
    print "%s %s" % (pkg, meta)
    drops[rtype] = [pkg, meta]

  return drops

def call (cmd):
  print cmd
  p = subprocess.Popen(cmd, shell=True)
  os.waitpid(p.pid, 0)

def build_deb (version, tag, rtypes, repo):
  call("/usr/bin/python setup.py sdist")
  shutil.copyfile("dist/foam-%s.tar.gz" % (version), "/tmp/foam-%s.tar.gz" % version)
  foamdir = os.getcwd()
  os.chdir("/tmp")
  try:
    shutil.rmtree("/tmp/foam-%s" % version)
  except OSError:
    pass
  call("tar -zxf foam-%s.tar.gz" % version)
  shutil.copytree("%s/debian" % foamdir, "/tmp/foam-%s/debian" % version)
  shutil.move("foam-%s.tar.gz" % version, "foam_%s.orig.tar.gz" % version)
  os.chdir("/tmp/foam-%s" % version)
  call("/usr/bin/debuild -uc -us")
  os.chdir("/tmp")
  for rtype in rtypes:
    try:
      os.makedirs("/tmp/%s/%s/all" % (repo, rtype))
    except os.error, e:
      continue

  for rtype in rtypes:
    try:
      os.remove("/tmp/%s/%s/all/foam_%s-%s_all.deb" % (repo, rtype, version, tag))
    except os.error, e:
      continue

  for rtype in rtypes:
    shutil.copy("/tmp/foam_%s-%s_all.deb" % (version, tag),
                "/tmp/%s/%s/all/" % (repo, rtype))
    call("/usr/bin/dpkg-scanpackages -m %s/%s | gzip -9c > /tmp/%s/%s/Packages.gz" % (
          repo, rtype, repo, rtype))

  os.chdir(foamdir)
  
def debchange (version, tag):
  call("/usr/bin/dch -v %s-%s \"New upstream\"" % (version, tag))

def repo_tag (version):
  call("/usr/local/bin/hg tag FOAM-%s" % version)

def fixup_setup (version, tag = None):
  f = open("setup.py", "r")
  new_setup = []
  for line in f.readlines():
    if line.count("version"):
      new_setup.append("      version='%s',\n" % version)
    else:
      new_setup.append(line)
  f.close()
  f = open("setup.py", "w+")
  f.write("".join(new_setup))

  f = open("src/foam/version.py", "w+")
  if tag is None:
    f.write("VERSION = '%s'\n" % (version))
  else:
    f.write("VERSION = '%s-%s'\n" % (version, tag))
  f.close()

def publish (val, drops, dialect):
  method,options = val.split(",", 1)
  if method == "s3":
    publish_s3(options, drops, dialect)
  else:
    print "Unknown method for publication: %s" % (method)

def publish_s3 (options, drops, dialect):
  from boto.s3.connection import S3Connection
  from boto.s3.key import Key

  bucket = options.strip()

  # You must set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
  # in your environment
  conn = S3Connection()
  b = conn.get_bucket(bucket)

  for repo,paths in drops.iteritems():
    for path in paths:
      k = Key(b)
      k.key = 'foam-pkg/%s/%s/all/%s' % (dialect, repo, os.path.basename(path))
      k.set_contents_from_filename(path)
      k.make_public()
      print "Uploaded %s to %s" % (path, k)
  

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("--version", dest="version")
  parser.add_option("--tag", dest="tag", default="1")
  parser.add_option("--rpm", dest="rpm", action="store_true", default=False)
  parser.add_option("--deb", dest="deb", action="store_true", default=False)
  parser.add_option("--dialect", dest="dialect", default="lucid")
  parser.add_option("--publish", dest="publish", default=None)
  (opts, args) = parser.parse_args()

  if opts.deb:
    drops = package_deb(opts)
  if opts.rpm:
    drops = package_rpm(opts)

  if opts.publish:
    publish(opts.publish, drops, opts.dialect)
