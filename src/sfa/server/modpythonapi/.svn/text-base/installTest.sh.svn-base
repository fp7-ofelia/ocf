GENI_SRC_DIR=/home/smbaker/projects/geniwrapper/trunk

mkdir -p /usr/local/testapi/bin
mkdir -p /usr/local/testapi/bin/sfa/trust
mkdir -p /usr/local/testapi/bin/sfa/util
mkdir -p /usr/local/testapi/var/trusted_roots
mkdir -p /repository/testapi

# source code for the API
cp BaseApi.py /usr/local/testapi/bin/
cp AuthenticatedApi.py /usr/local/testapi/bin/
cp TestApi.py /usr/local/testapi/bin/API.py
cp ModPython.py /usr/local/testapi/bin/
cp ApiExceptionCodes.py /usr/local/testapi/bin/

# trusted root certificates that match gackstestuser.*
cp trusted_roots/*.gid /usr/local/testapi/var/trusted_roots/

# apache config file to enable the api
cp testapi.conf /etc/httpd/conf.d/

# copy over geniwrapper stuff that we need
echo > /usr/local/testapi/bin/sfa/__init__.py
echo > /usr/local/testapi/bin/sfa/trust/__init__.py
echo > /usr/local/testapi/bin/sfa/util/__init__.py
cp $GENI_SRC_DIR/sfa/trust/gid.py /usr/local/testapi/bin/sfa/trust/
cp $GENI_SRC_DIR/sfa/trust/certificate.py /usr/local/testapi/bin/sfa/trust/
cp $GENI_SRC_DIR/sfa/trust/trustedroot.py /usr/local/testapi/bin/sfa/trust/
cp $GENI_SRC_DIR/sfa/trust/credential.py /usr/local/testapi/bin/sfa/trust/
cp $GENI_SRC_DIR/sfa/trust/rights.py /usr/local/testapi/bin/sfa/trust/
cp $GENI_SRC_DIR/sfa/util/faults.py /usr/local/testapi/bin/sfa/util/ 

# make everything owned by apache
chown -R apache /usr/local/testapi
chown apache /etc/httpd/conf.d/testapi.conf

/etc/init.d/httpd restart