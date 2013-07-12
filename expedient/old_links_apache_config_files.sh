#!/bin/bash

cd /etc/apache2/conf.d/
sudo mv vhost-macros.conf _vhost-macros.conf.REFACTOR
sudo mv _vhost-macros.conf.ORIGINAL vhost-macros.conf

cd /etc/apache2/sites-available
sudo mv expedient.conf _expedient.conf.REFACTOR
sudo mv _expedient.conf.ORIGINAL expedient.conf

