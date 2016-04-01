#!/bin/bash

apt_src_list=/etc/apt/sources.list
etc_hosts=/etc/hosts
sudoers_file=/etc/sudoers


# Skip if a) sudo package is installed or b) image is not Debian 6
([[ ! -z $(dpkg | grep sudo) ]] || [[ -z $(uname -a | grep "2.6.32-5-xen") ]] ) && return 0

if [ ! -f $apt_src_list.bak ]; then
  sed -i 's/^/#/' $apt_src_list
  mv $apt_src_list $apt_src_list.bak
  echo """
#
# Updated sources
#
deb http://httpredir.debian.org/debian/ wheezy main contrib non-free
deb-src http://httpredir.debian.org/debian/ wheezy main contrib non-free

deb http://security.debian.org/ wheezy/updates main contrib non-free
deb-src http://security.debian.org/ wheezy/updates main contrib non-free

deb http://httpredir.debian.org/debian wheezy-updates main contrib non-free
deb-src http://httpredir.debian.org/debian wheezy-updates main contrib non-free
""" > $apt_src_list
fi

apt-key update

# Non-supported keys
declare -a err_keys=("8B48AD6246925553" "9D6D8F6BC857C906" "7638D0442B90D010" "6FB2A1C265FFB764")
for i in "${err_keys[@]}"
do
  gpg --keyserver pgpkeys.mit.edu --recv-key "$i"      
  gpg -a --export "$i" | apt-key add -
done

# Lack of sudo
apt-get update -y

mv $sudoers_file $sudoers_file.bak
apt-get install sudo -y
mv $sudoers_file $sudoers_file.orig
mv $sudoers_file.bak $sudoers_file

# Warning on sudo
hostname=$(hostname)
[[ -z $(grep "127.0.0.1    $hostname" $etc_hosts) ]] && echo "127.0.0.1    $hostname" >> $etc_hosts

# SSH connection
ifconfig eth0 mtu 1496
ifconfig eth1 mtu 1496
ifconfig eth2 mtu 1496
