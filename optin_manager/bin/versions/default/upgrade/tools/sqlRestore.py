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

cfg = ConfigObj(sys.argv[1]+".cfg")

section = cfg['General']

#Droping the database and recreating

#Preparing command
command =''

if section["user"] != "":
	command+=" --user="+ section["user"]
if section["password"] != "":
	command+=" --password="+ section["password"]
if section["host"] != "":
	command+=" --host="+ section["host"]
if section["port"] != "":
	command+=" --port="+ section["port"]

command+=" "+section["database"]

if section["host"] == "":
	host="localhost"
else:
	host=section["host"]

dropDB="mysql -e \"drop database "+section["database"]+"; CREATE DATABASE "+section["database"]+";GRANT ALL ON "+section["database"]+" . * TO '"+section["user"]+"'@'"+host+"';\""+command 

print dropDB

if os.system(dropDB)>0:
	sys.exit(1)

importDB="mysql "+command+" < "+sys.argv[1]

print importDB

sys.exit(os.system(importDB))
