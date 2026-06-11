#!/bin/bash

mkdir -p ./certs

echo "---> Generating private keys for a certificate authority and a broker"
openssl genrsa -out ./certs/ca.key 4096
openssl genrsa -out ./certs/broker.key 4096

echo "---> Generating certificate authority certificate"
openssl req -new -x509 -days 1000 -key ./certs/ca.key -out ./certs/ca.crt

echo "---> Generating broker's certificate request"
echo "    ---> Common Name must be valid IP address of machine where mosquitto server is going to be running"
openssl req -new -out ./certs/broker.csr -key ./certs/broker.key

echo "---> Signing certificate"
openssl x509 -req -in ./certs/broker.csr -CA ./certs/ca.crt -CAkey ./certs/ca.key -CAcreateserial -out ./certs/broker.crt -days 1000

echo "---> Cleaning"
rm -rf ./certs/broker.csr ./certs/ca.srl

echo "---> Distributing certificates"
cp ./certs/ca.crt ./AAU/certs/ca.crt
cp ./certs/broker.key ./AAU/certs/broker.key
cp ./certs/broker.crt ./AAU/certs/broker.crt

cp ./certs/ca.crt ./AU/certs/ca.crt
cp ./certs/broker.key ./AU/certs/broker.key
cp ./certs/broker.crt ./AU/certs/broker.crt

cp ./certs/ca.crt ./ks-smart-systems-skill/scripts/certs/ca.crt
cp ./certs/broker.key ./ks-smart-systems-skill/scripts/certs/broker.key
cp ./certs/broker.crt ./ks-smart-systems-skill/scripts/certs/broker.crt

echo "DONE"