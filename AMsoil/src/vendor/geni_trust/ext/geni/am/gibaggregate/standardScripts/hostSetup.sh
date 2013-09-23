#!/bin/bash

#----------------------------------------------------------------------
# Copyright (c) 2012-2013 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------


# This script should be run just ONE TIME to configure the host container.
# This script is run as part of the process of setting up a VirtualBox VM 
#  with GENI-in-a-Box.  GENI-in-a-Box users should not have to run this script.


# Copy the .desktop file to the proper place so the gib-startup.sh script is run when the user logs in
mkdir -p ~/.config/autostart
cp ~/gcf/gib-config-files/gibStart.desktop ~/.config/autostart

# Make the .gcf directory and copy the gcf_config and omni_config files into
#    this directory
mkdir ~/.gcf
cp ~/gcf/gib-config-files/gcf_config ~/.gcf
cp ~/gcf/gib-config-files/omni_config ~/.gcf

# Add ~/gcf/src to the user's path
echo "" >> ~/.bash_profile
echo "# Lines added by GENI-in-a-Box setup script" >> ~/.bash_profile
echo "PATH=$PATH:$HOME/bin:$HOME/gcf/src" >> ~/.bash_profile
echo "export PATH" >> ~/.bash_profile

# Create keys for default user with empty passphrase.  Move the private key
#   to the .ssh directory
ssh-keygen -t rsa -N "" -f ~/.gcf/$USER
mkdir -p ~/.ssh
mv ~/.gcf/$USER ~/.ssh/id_rsa

# Install the Python packages needed by gcf 
sudo yum install m2crypto python-dateutil pyOpenSSL xmlsec1 xmlsec1-devel xmlsec1-openssl xmlsec1-openssl-devel

# TO DO: Add entry for $USER in omni_config.  For now this will be a manual
#    step.

# Run gen-certs to create CH, AM and user certs.
~/gcf/src/gen-certs.py --notAll --ch
~/gcf/src/gen-certs.py --notAll --am
~/gcf/src/gen-certs.py --notAll --exp -u $USER

# Extract the password for the user accounts in the VMs created by createsliver
#   and write it to ~/.gcf/passwords
echo "The following accounts share the same password:" > ~/.gcf/passwords
echo "    - root on the GENI-in-a-Box VM," >>  ~/.gcf/passwords
echo "    - gib account (the GENI-in-a-Box account you are automatically logged into)," >> ~/.gcf/passwords 
echo "    - root on the experimenter nodes," >>  ~/.gcf/passwords
echo "    - user accounts on the experimenter nodes." >>  ~/.gcf/passwords
echo "" >> ~/.gcf/passwords
echo "The password is:" >> ~/.gcf/passwords
echo -n "    " >> ~/.gcf/passwords
grep -i "rootpwd" ~/gcf/src/geni/am/gibaggregate/config.py | awk '{print $3}' | sed "s/'//g" >> ~/.gcf/passwords
echo "" >> ~/.gcf/passwords
echo "Please do not change this password." >> ~/.gcf/passwords
 
# Copy example rspec files to ~/geni-in-a-box
cp -r ~/gcf/rspec-examples ~/geni-in-a-box

# Install the brctl package
sudo yum -y install /usr/sbin/brctl

# Add /etc/host entries so the GENI-in-a-Box aggregate manager and 
#    resources can be referenced by name.
# Save current copy of /etc/hosts
sudo cp /etc/hosts /etc/hosts.save 
# Add geni-in-a-box.net as an alias for localhost
sudo sh -c "cat /etc/hosts.save | sed 's/127.0.0.1[[:space:]]*localhost.localdomain[[:space:]]*localhost/& geni-in-a-box.net/' > /etc/hosts"
# Add entries for the VMs.  Use the IP address on the control network
sudo sh -c "echo '10.0.1.101 pc101.geni-in-a-box.net pc101' >> /etc/hosts"
sudo sh -c "echo '10.0.1.102 pc102.geni-in-a-box.net pc102' >> /etc/hosts"
sudo sh -c "echo '10.0.1.103 pc103.geni-in-a-box.net pc103' >> /etc/hosts"
sudo sh -c "echo '10.0.1.104 pc104.geni-in-a-box.net pc104' >> /etc/hosts"
sudo sh -c "echo '10.0.1.105 pc105.geni-in-a-box.net pc105' >> /etc/hosts"
sudo sh -c "echo '10.0.1.106 pc106.geni-in-a-box.net pc106' >> /etc/hosts"
