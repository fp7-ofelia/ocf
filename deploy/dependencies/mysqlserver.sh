#!/bin/bash

###
#    @author: CarolinaFernandez
#    @organization: i2CAT
#    @project: Ofelia FP7
#    @description: script to install MySQL-server and create the databases
###


if [[ $(dpkg -l | grep mysql-server) != "" ]]; then
    echo "MySQL server already installed. Skipping..."
    exit 1
else
    apt-get install mysql-server
fi

ocf_modules=("expedient" "optin_manager" "vt_manager")
prefix_database="ocf__"

while [[ $user == "" ]]
    do
        echo ""
        echo "Please provide your MySQL credentials in order to configure it for OCF"
        read -p "User: " user
        #user=${user:-root}
        echo -n Password: 
        read -s password
        echo ""
done

for module in "${ocf_modules[@]}"
    do
        mysql -u $user -p$password --execute="CREATE DATABASE $prefix_database$module;"
        mysql -u $user -p$password --execute="GRANT ALL ON $prefix_database$module.* to $user@127.0.0.1 IDENTIFIED BY '$password';"
done

echo "MySQL databases successfully created"
