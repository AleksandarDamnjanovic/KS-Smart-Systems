#!/bin/bash

echo "--->Old mosquitto configuration cleaning initialized..."

rm -f /etc/mosquitto/users.conf
rm -rf /etc/mosquitto/ca_certificates
rm -rf /etc/mosquitto/certs
rm -rf /etc/mosquitto/conf.d

if [ -f "/etc/mosquitto/mosquitto-backup.conf" ]; then
    mv "/etc/mosquitto/mosquitto-backup.conf" "/etc/mosquitto/mosquitto.conf"
fi

echo "--->Cleaning DONE"