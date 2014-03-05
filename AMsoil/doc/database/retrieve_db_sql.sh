#!/bin/bash

# Note: modify $user and $password as needed
user=""
password=""

sudo mysqldump -u $user -p$password --opt vt_manager > vtm.sql
sudo mysql -u $user -p$password --execute="CREATE DATABASE IF NOT EXISTS vtm;"
#sudo mysql -u $user -p$password vtm < vt_manager.sql
#sudo rm vt_manager.sql
