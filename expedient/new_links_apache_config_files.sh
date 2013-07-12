#!/bin/bash

##
# To move later to OFVER's upgrade. OFVER's install shall be slightly modified too.
#

cd /etc/apache2/conf.d/
sudo mv vhost-macros.conf _vhost-macros.conf.ORIGINAL
if [ -f _vhost-macros.conf.REFACTOR ]; then
	sudo mv _vhost-macros.conf.REFACTOR vhost-macros.conf
else
	sudo ln -s /opt/ofelia/expedient/conf/apache/vhost-macros.conf vhost-macros.conf
fi

cd /etc/apache2/sites-available
sudo mv expedient.conf _expedient.conf.ORIGINAL
if [ -f _expedient.conf.REFACTOR ]; then
	sudo mv _expedient.conf.REFACTOR expedient.conf
else
	sudo ln -s /opt/ofelia/expedient/conf/apache/vhost-clearinghouse.conf expedient.conf
fi

