#!/bin/sh

###
#    @author: CarolinaFernandez
#    @organization: i2CAT
#    @project: Ofelia FP7
#    @description: script to install a specific FlowVisor release and configure according to our needs
###


FLOWVISOR_RELEASE="1.4.0-1"

# 1. Obtain public key
wget http://updates.onlab.us/GPG-KEY-ONLAB

# 2. Install the repository public key
apt-key add GPG-KEY-ONLAB

# 3. Add the following line to /etc/apt/sources.list (if not already there)
if [ ! $(grep "deb http://updates.onlab.us/debian" /etc/apt/sources.list | grep -v "^#") ]; then
    echo """# Release - the latest and greatest
deb http://updates.onlab.us/debian stable/
# Staging - what's coming next
deb http://updates.onlab.us/debian staging/
# Nightly - the bleeding edge
deb http://updates.onlab.us/debian unstable/""" >> /etc/apt/sources.list
fi

# 4. Update your apt database
apt-get update

# 5. Install chosen version of FlowVisor
apt-get install flowvisor=$FLOWVISOR_RELEASE

# 6. Modify to meet our requirements
# Correct permissions in order to be able to pass this point and write to the DB
chmod 755 /usr/share/db/flowvisor/derby.log
# Modify log configuration to avoid writing on stdout
sed -i -e "s/log4j.rootCategory=WARN, system/#log4j.rootCategory=WARN, system\nlog4j.rootCategory=WARN/" /etc/flowvisor/fvlog.config
