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
command = ""
# User must be 'root' in order to successfully backup the database.
command_root = " --user='root' --password"

if section["user"] != "":
	command+=" --user='"+ section["user"]+"'"
if section["password"] != "":
	command+=" --password='"+ section["password"]+"'"
if section["host"] != "":
	command += " --host=" + section["host"]
	command_root += " --host=" + section["host"]
if section["port"] != "":
	command +=" --port=" + section["port"]
	command_root +=" --port=" + section["port"]

command += " " + section["database"] + " < " + sys.argv[1]
command_root += " " + section["database"] + " < " + sys.argv[1]

if section["host"] == "":
        host = "localhost"
else:
        host = section["host"]

# Island Manager will be prompted to enter the root's password for the backup
dropDB = "mysql -e \"drop database " + section["database"] + "; create database " + section["database"] + "; grant all on " + section["database"] + ".* to '" + section["user"] + "'@'" + host + "';\"" + command_root
print dropDB

print "\nPlease input your MySQL root password in order to perform a backup of %s..." % str(section["database"])
if os.system(dropDB)>0:
        sys.exit(1)

importDB = "mysql" + command + " < " + sys.argv[1]
print importDB
sys.exit(os.system(importDB))
