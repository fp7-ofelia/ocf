#!/bin/bash
CURRENT_PWD=$PWD
#Creating certs
cd ../security/certs/ && make
cd $CURRENT_PWD

#Settings
echo ""
echo "Configuring settings file"
echo "-----------------"
echo "Please type a STRONG password for the XML-RPC interface of the agent."
echo "This password will be the one asked to introduce once you add the server to the Manager"
echo "Alert!!! Password will be shown in clear"
echo -n "password:"
read VALUE;

#Substitute password in settings
/bin/sed -e "s/#XMLRPC_SERVER_PASSWORD=\"changeAndUncommentMe\"/XMLRPC_SERVER_PASSWORD=\"$VALUE\"/" ../mySettings-example.py > ../mySettings.py

#Show settings
echo ""
echo "Now settings will be shown. Please modify them manually for specific configurations"
cat ../mySettings.py
#echo "Valor: $VALUE"
