import os
import sys
from os.path import dirname, join
from django.conf import * 

#configobj
try:
	from configobj import ConfigObj
except:
	#FIXME: ugly
	os.system("apt-get update && apt-get install python-configobj -y")
	from configobj import ConfigObj


PYTHON_DIR = join(dirname(__file__), '../../../../../src/python')

# This is needed because wsgi disallows using stdout
sys.stdout = sys.stderr

#os.environ['DJANGO_SETTINGS_MODULE'] = 'expedient.clearinghouse.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = sys.argv[2]

#sys.path.append(PYTHON_DIR)
sys.path.insert(0,PYTHON_DIR)


##Retrive Django settings
#print settings.DATABASE_NAME 
#print settings.DATABASE_USER
#print settings.DATABASE_PASSWORD 
#print settings.DATABASE_HOST 
#print settings.DATABASE_PORT

command="mysqldump --databases "+settings.DATABASE_NAME

if settings.DATABASE_USER != "":
	command+=" --user='"+settings.DATABASE_USER+"'" 

if settings.DATABASE_PASSWORD != "":
	command+=" --password='"+settings.DATABASE_PASSWORD+"'"

if settings.DATABASE_HOST != "":
	command+=" --host="+settings.DATABASE_HOST
if settings.DATABASE_PORT != "":
	command+=" --port="+settings.DATABASE_PORT

command+=" > "+str(sys.argv[1])

#Store settings so that it is not messed up in the upgrade
cfg = ConfigObj(sys.argv[1]+'.cfg')

generalSection = {
    'database': settings.DATABASE_NAME,
    'user':settings.DATABASE_USER, 
    'password':settings.DATABASE_PASSWORD, 
    'host':settings.DATABASE_HOST,
    'port':settings.DATABASE_PORT, 
}

cfg['General'] = generalSection
cfg.write()

#Dump DB
print "Trying to dump DB using: "+command
sys.exit(os.system(command))
