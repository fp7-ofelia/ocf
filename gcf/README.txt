
Description
===========

This software implements a sample GENI Aggregate Manager. It also
includes a sample GENI Clearinghouse and command line client. This
software is intended to demonstrate the GENI Aggregate Manager API.


Software Dependencies
=====================

This software requires a number of readily available software
packages.

1. Python M2Crypto package

  The M2Crypto package provides utilities for handling X.509
  certificates and SSL connections. M2Crypto is required by
  certificate class in sfa/trust. M2Crypto should be readily available
  on most Linux distributions.

  More information is available at:
    http://chandlerproject.org/bin/view/Projects/MeTooCrypto

2. Python dateutil package

  The dateutil package provides date parsing routines to Python. It
  should be readily available on most Linux distributions.

  More information is available at:
    http://labix.org/python-dateutil

3. xmlsec1 package

  The XML Security Library provides implementations of XML Digital
  Signature (RFC 3275) and W3C XML Encryption. The program xmlsec1
  from this package is used to sign credentials.  

  More information is available at:
    http://www.aleksey.com/xmlsec/
    http://www.w3.org/TR/xmlenc-core/
    http://www.ietf.org/rfc/rfc3275.txt


Included Software
=================

This package includes software from PlanetLab. All of the PlanetLab
software is in the src/sfa directory. More information, including the
license, can be found in src/sfa/README.txt.


Instructions
============

1. Initialize the certificate authority and generate keys and certificates:

 $ src/init-ca.py

 This creates a certificate authority key and certificate and then
 creates keys and certificates for a clearinghouse (ch), an aggregate
 manager (am), and a researcher (alice).

2. Start the clearinghouse server:

 $ src/gch.py -r ca-cert.pem -c ch-cert.pem -k ch-key.pem

3. Start the aggregate manager server:

 $ src/gam.py -r ca-cert.pem -c am-cert.pem -k am-key.pem

4. Run the client

 $ src/client.py -c alice-cert.pem -k alice-key.pem \
     --ch https://localhost:8000/ --am https://localhost:8001/

 The output should show some basic API testing, and possibly some
 debug output.
