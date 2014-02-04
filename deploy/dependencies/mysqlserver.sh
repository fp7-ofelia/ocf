#!/bin/bash

###
#    @author: CarolinaFernandez
#    @organization: i2CAT
#    @project: Ofelia FP7
#    @description: script to install MySQL-server and create the databases
###


if [[ $(dpkg -l | grep mysql-server) != "" ]]; then
    echo "MySQL server already installed. Skipping..."
#    exit 1
else
    apt-get install mysql-server
fi

ocf_modules=("expedient" "optin_manager" "vt_manager")
prefix_database="ocf__"
host="localhost"

## Ask for root and user credentials
while [[ $user_root == "" ]]
    do
        echo ""
        echo "Provide your MySQL root credentials in order to create the OCF databases"
        read -p "MySQL root user: " user_root
        #user=${user:-root}
        echo -n Password: 
        read -s password_root
        echo ""
done  
while [[ $user == "" ]]
    do
        echo ""
        echo "Credentials for the user with access the OCF databases (if doubtful use the previous ones)"
        read -p "User: " user
        echo -n Password: 
        read -s password
        echo ""
done

## Create user if it does not exists
if [[ $(mysql -u $user_root -p$password_root --execute="SELECT * FROM mysql.user WHERE User='$user';") == "" ]]; then
    mysql -u $user_root -p$password_root --execute="CREATE USER '$user'@$host IDENTIFIED BY '$password';"
    echo "Creating MySQL user $user@$host"
fi

for module in "${ocf_modules[@]}"
    do
        mysql -u $user_root -p$password_root --execute="CREATE DATABASE IF NOT EXISTS $prefix_database$module;"
        mysql -u $user_root -p$password_root --execute="GRANT ALL ON $prefix_database$module.* to $user@$host IDENTIFIED BY '$password';"
        echo "Granting privileges on $prefix_database$module.* to $user@$host"
done

echo "MySQL databases successfully created"
