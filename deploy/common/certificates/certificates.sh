#!/bin/bash

# XXX: Move somewhere else
#source ../utils/utils.sh

###
# Check if certificates are installed under /etc/apache2/ssl.crt/
#   1 - Installed: check that these are GIDs (check extensions)
#     1.1 - If GIDs, do nothing
#     1.2 - If no GIDs, parse current certificates and generate GIDs from them
#   2 - Not installed: generate from scratch (check code under ofver's lib/ssl/)
###

# 1. Check if installation = OFELIA

cd $PWD

accept_generate_certificates=0
can_parse_certs=true

server_cert_file=/etc/apache2/ssl.crt/server.crt
ca_cert_file=/etc/apache2/ssl.crt/ca.crt

if [[ ! -f $ca_cert_file ]] && [[ ! -f $server_cert_file ]]; then
    $can_parse_certs=false
    accept_generate_certificates="y"
    echo "Certificates not found: preparing to generate new ones..."

else
   isGID=$(openssl x509 -text -in $ca_cert_file  -noout | grep "X509v3 Subject Alternative Name:")
   if [[ ! -z "$isGID" ]]; then
      echo "There were found GID-based certificates already"
      exit 1
   else

      while [[ ! $accept_generate_certificates =~ ^[y|Y|n|N]$ ]]
          do
              echo "Do you wish to generate GID-based certificates? [y/N]"
              read accept_generate_certificates
              if [[ ! $accept_generate_certificates =~ ^[y|Y|n|N]$ ]]; then
                  echo "Please accept (\"y\") or reject (\"n\") the generation"
              fi
              if [[ $accept_generate_certificates =~ ^[n|N]$ ]]; then
                  echo "Certificate generation aborted by user"
                  exit 1
              fi
          done
   fi
fi


# XXX: Perform generation of GIDs

while [[ ! $ofelia_install =~ ^[y|Y|n|N]$ ]]
    do
        echo "Is this an OFELIA installation? [y/N]"
        read ofelia_install
        if [[ ! $ofelia_install =~ ^[y|Y|n|N]$ ]]; then
            echo "Please say yes (\"y\") or no (\"n\")"
        fi
    done

if [[ $ofelia_install =~ ^[n|N]$ ]]; then
   
   URI_AUTHORITY="'URI:urn:publicid:IDN+fibre+authority+sa'"
   URI_SUBAUTHORITY="'URI:urn:publicid:IDN+fibre:am+cm'"
else
 
   URI_AUTHORITY="'URI:urn:publicid:IDN+ofelia+authority+sa'"
   URI_SUBAUTHORITY="'URI:urn:publicid:IDN+ofelia:am+cm'"
fi

function parse_cert {
   #Pass the cerificate file location in the first arg
   #Pass the config_file location as second arg
   #Pass the URI_AUTHORITY as third arg

   PARSED_COUNTRY=$(openssl x509 -in $1 -noout -text | grep "Subject:" | grep -oPm1 "(?<=C=)[^<]+" | cut -d"," -f1)
   PARSED_OU=$(openssl x509 -in $1 -noout -text | grep "Subject:" | grep -oPm1 "(?<=OU=)[^<]+" | cut -d"," -f1)
   PARSED_ORG=$(openssl x509 -in $1 -noout -text | grep "Subject:" | grep -oPm1 "(?<=O=)[^<]+" | cut -d"," -f1)
   PARSED_CN=$(openssl x509 -in $1 -noout -text | grep "Subject:" | grep -oPm1 "(?<=CN=)[^<]+" | cut -d"," -f1| cut -d "/" -f1)
   PARSED_EMAIL=$(openssl x509 -in $ca_cert_file -noout -text | grep "Subject:" | grep -oPm1 "(?<=CN=)[^<]+" | cut -d"," -f1 | cut -d "/" -f2 | cut -d "=" -f2)
   URI_HEADER="URI:urn:uuid:"
   UUID=$(python  -c 'import uuid; print uuid.uuid4()')
   URI_UUID="'"$URI_HEADER$UUID"'"
   EMAIL_STR="email:"
   EMAIL_SET="'"$EMAIL_STR$PARSED_EMAIL"'"
   SUBJECT_ALT_NAME="$3,$URI_UUID,$EMAIL_SET"

   populate_config_file $2 $PARSED_CN $PARSED_OU $PARSED_ORG $PARSED_COUNTRY $SUBJECT_ALT_NAME

}

function create_cert {
   #Pass the certificate_config file as first argument
   #Pass the URI_AUTHORITY as second param
   echo "Please enter the following Certificate params" 
   read -p "Common Name (CN): " cn
   read -p "Organizational Unit Name (OU): " ou
   read -p "Organization (O): " org
   read -p "Country (C): "  count
   read -p "Email: "  email 
   CREATED_URI_HEADER="URI:urn:uuid:"
   CREATED_UUID=$(python  -c 'import uuid; print uuid.uuid4()')
   CREATED_URI_UUID="'"$CREATED_URI_HEADER$CREATED_UUID"'"
   CREATED_EMAIL_STR="email:"
   CREATED_EMAIL_SET="$CREATED_EMAIL_STR$email"
   CREATED_SUBJECT_ALT_NAME="$2,$CREATED_URI_UUID,$CREATED_EMAIL_SET"
   populate_config_file $1 $cn $ou $org $count $CREATED_SUBJECT_ALT_NAME

}

function populate_config_file {
   #Pass the config file location as firs arg
   #Pass the CN as second arg
   #Pass the OU as third arg
   #Pass the O as fourth arg
   #Pass the C as fith arg
   #pass the subjectAltName as sixth arg
   sed -i "s/\(CN *= *\).*/\1$2/g" $1
   sed -i "s/\(OU *= *\).*/\1$3/g" $1
   sed -i "s/\(O *= *\).*/\1$4/g" $1
   sed -i "s/\(C *= *\).*/\1$5/g" $1
   sed -i "s/\(subjectAltName *= *\).*/\1$6/g" $1
}

cp ca_cert.conf ca_cert_copy.conf
cp server_cert.conf server_cert_copy.conf
ca_config_file="ca_cert_copy.conf"
server_config_file="server_cert_copy.conf"

if [[  $can_parse_certs==true ]]; then
   parse_cert $ca_cert_file $ca_config_file $URI_AUTHORITY
   parse_cert $server_cert_file $server_config_file $URI_SUBAUTHORITY

else
   echo "Setting up CA parameters"
   create_cert $ca_config_file $URI_AUTHORITY
   echo "Setting up Server parameters"
   create_cert $server_config_file $URI_SUBAUTHORITY

fi

#Generating the certificates

#Generate CA key
openssl genrsa  -out ca.key 4096

#Generate signature request for CA
openssl req -new -nodes -config $ca_config_file > ca.csr

#Generate CA certificate with extensions
openssl x509 -extfile $ca_config_file -extensions ca_extensions -sha1 -req -signkey ca.key -days 7300 < ca.csr > ca.crt

#Generate server key
openssl genrsa  -out server.key 4096

#Generate signature request for server to CA 
openssl req -new -nodes -key server.key -config $server_config_file > server.csr

#Generate server certificate with extensions signed by CA
openssl x509 -extfile $server_config_file -extensions cert_extensions  -sha1  -req -CAcreateserial -CAkey ca.key -CA ca.crt -days 3650 < server.csr > server.crt


echo cleaning directory...
rm -rf *.csr
mv *.crt /etc/apache2/ssl.crt
mv *.key /etc/apache2/ssl.key

rm $server_config_file
rm $ca_config_file 

echo "Certificates successfully generated"
