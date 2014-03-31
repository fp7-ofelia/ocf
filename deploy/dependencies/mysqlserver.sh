#!/bin/bash

###
#    @author: CarolinaFernandez
#    @organization: i2CAT
#    @project: Ofelia FP7
#    @description: script to install MySQL-server and create the databases
###


# XXX: Move somewhere else
source ../utils/utils.sh

if [[ $(dpkg -l | grep mysql-server) != "" ]]; then
    warning "MySQL server already installed. Skipping..."
else
    apt-get -y install mysql-server
fi

#ocf_modules=("expedient" "optin_manager" "vt_manager")
ocf_modules=$@
# Replace all "[", "]", ",", "'" by a space
ocf_modules=${ocf_modules//[\[\]\,\']/ }
# Create array from list
ocf_modules=($ocf_modules)
# TODO fix and call method 'list_to_array'
#source ../utils/utils.sh
#ocf_modules=$(list_to_array "$ocf_modules")

prefix_database="ocf__"
host="localhost"

## Ask for root and user credentials
while [[ $user_root == "" ]]
    do
        echo ""
        print "Provide your MySQL root credentials in order to create the OCF databases"
        read -p "MySQL root user: " user_root
        #user=${user:-root}
        echo -n Password: 
        read -s password_root
        echo ""
done  
while [[ $user == "" ]]
    do
        echo ""
        print "Credentials for the user with access the OCF databases (if doubtful use the previous ones)"
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
        echo "CREATE DATABASE IF NOT EXISTS $prefix_database$module;"
        mysql -u $user_root -p$password_root --execute="GRANT ALL ON $prefix_database$module.* to $user@$host IDENTIFIED BY '$password';"
        echo "Granting privileges on $prefix_database$module.* to $user@$host"
done

success "MySQL databases successfully created"
