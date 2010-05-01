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
