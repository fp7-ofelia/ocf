#!/bin/bash
openssl genrsa -out server.key -des3 1024
openssl req -new -key server.key -out server.csr
openssl req -new -x509 -days 1460 -key server.key -out server.crt
openssl rsa -in server.key -out server_wo_pw.key
