openssl genrsa -des3 -out server.key 2048
openssl req -new -key server.key -out server.csr
mv server.key server.key.passprotect
openssl rsa -in server.key.passprotect -out server.key
rm server.key.passprotect
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt
rm server.csr

