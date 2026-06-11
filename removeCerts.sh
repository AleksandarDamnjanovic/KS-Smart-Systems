#!/bin/bash

rm ./certs/ca.crt 
rm ./AAU/certs/ca.crt
rm ./certs/broker.key
rm ./AAU/certs/broker.key
rm ./certs/broker.crt
rm ./AAU/certs/broker.crt
rm ./AU/certs/ca.crt
rm ./AU/certs/broker.key
rm ./AU/certs/broker.crt
rm ./ks-smart-systems-skill/scripts/certs/ca.crt
rm ./ks-smart-systems-skill/scripts/certs/broker.key
rm ./ks-smart-systems-skill/scripts/certs/broker.crt
rm -rf ./certs

echo "---> DONE"