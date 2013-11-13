from distutils.core import setup
import os.path
import os
import pprint
import glob
import fnmatch

def generatePluginFiles ():
  pfiles = []
  foamroot = "/opt/ofelia/ofam/local"
  pdirs = os.listdir(os.getcwd() + "/plugins")
  for pd in pdirs:
    dl = []
    for plgfile in os.listdir(os.getcwd() + "/plugins/%s/" % (pd)):
      dl.append("plugins/%s/%s" % (pd, plgfile))
    pfiles.append(("%s/plugins/%s" % (foamroot, pd), dl))
  return pfiles

def generateDataDir (cur_dir_loc):
  files = []
  for f in os.listdir(os.getcwd() + "/%s" % (cur_dir_loc)):
    files.append("%s/%s" % (cur_dir_loc, f))
  return files

def opj (*args):
  # Handy utility from Robin Dunn
  path = os.path.join(*args)
  return os.path.normpath(path)

# distutils should include this function...
def generateDataFiles (srcdir, *wildcards, **kw):
  def walkHelper (arg, dirname, files):
    #print dirname
    names = []
    lst, wildcards, newroot, srclen = arg
    for wc in wildcards:
      wc_name = opj(dirname, wc)
      for f in files:
        filename = opj(dirname, f)
        if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
          names.append(filename)
    if names:
      lst.append(("%s/%s" % (newroot, dirname[srclen:]), names))

  file_list = []
  recursive = kw.get('recursive', True)
  newroot = kw.get('newroot', srcdir)
  if recursive:
    os.path.walk(srcdir, walkHelper, (file_list, wildcards, newroot, len(srcdir)))
  else:
    walkHelper((file_list, wildcards, newroot, len(srcdir)), srcdir,
               [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
  return file_list


def main ():
  data_files=[('/opt/ofelia/ofam/local/sbin', ['src/scripts/foam.fcgi']),
              ('/opt/ofelia/ofam/local/bin', ['src/scripts/expire', 'src/scripts/expire-emails', 'src/scripts/daily-queue']),
              ('/opt/ofelia/ofam/local/schemas', ['schemas/ad.xsd', 'schemas/request.xsd', 'schemas/of-resv-3.xsd',
                                     'schemas/any-extension-schema.xsd', 'schemas/request-common.xsd',
                                     'schemas/of-resv-4.xsd']),
              ('/etc/nginx/sites-available/', ['src/foam.conf'])]
  data_files.extend(generatePluginFiles())
  data_files.extend(generateDataFiles('src/foamext/', "*.py", newroot='/opt/ofelia/ofam/local/lib/foamext'))
  data_files.extend(generateDataFiles('src/ext/', "*.py", newroot='/opt/ofelia/ofam/local/lib'))
  #data_files.extend(generateDataFiles('src/foam/', "*.py", newroot='/opt/ofelia/ofam/local/lib/foam'))
  data_files.extend(generateDataFiles('src/foam/', "*.*", newroot='/opt/ofelia/ofam/local/lib/foam'))
  data_files.extend(generateDataFiles('templates/', "*.txt", newroot='/opt/ofelia/ofam/local/etc/templates/default'))
#  pprint.pprint(data_files)

  setup(name='foam',
      version='foam_0.8.2|ofelia_0.1',
        description='Flowvisor Openflow Aggregate Manager',
        author='Nick Bastin and Vasileios Kotronis',
        author_email='nick.bastin@gmail.com',
        url='https://openflow.stanford.edu/display/FOAM/Home',
        packages=[],
        package_dir={'foam': 'src/foam',
                     'jsonrpc' : 'src/ext/jsonrpc',
                     'sfa' : 'src/ext/sfa',
                     'geni' : 'src/ext/geni'},
        scripts=['src/scripts/foamctl', 'src/scripts/foam-db-convert.py'],
        data_files = data_files
       )

if __name__ == '__main__':
  main()
