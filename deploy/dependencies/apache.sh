#!/bin/bash

###
#    @author: CarolinaFernandez
#    @organization: i2CAT
#    @project: Ofelia FP7
#    @description: script to install Apache2 and potentially its CA and server certificates
###


# XXX: Move somewhere else
source ../utils/utils.sh

# If dpkg shows entry with $FLOWVISOR_RELEASE on it, do not install
if [[ $(dpkg -l | grep "apache2") != "" ]]; then
    warning "Apache2 already installed. Skipping..."
    exit 1
else
    apt-get -y install apache2
fi

# TODO: set certificates generation here instead per AM
# Copy from <am_path>/bin/versions/default/install/lib/ssl

success "Apache2 successfully installed"
