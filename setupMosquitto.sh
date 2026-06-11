#!/bin/bash

# /etc/mosquitto/users.conf this file contains, users and passwords for mosquitto server
# by default you have two users. One is necessary and that is admin. user 1f is here just for an example
# you are free to change this part according to your needs
# user names and passwords are provided in this way name:password

# This script needs 1 argument and that is IP address of the mqtt broker

echo "---> Mosquitto setting up initialized..."

echo "---> Backing up original configuration..."
cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto-backup.conf

echo "---> Generating users..."
touch /etc/mosquitto/users.conf
echo "admin:000000" >> /etc/mosquitto/users.conf
echo "1f:000000" >> /etc/mosquitto/users.conf
mosquitto_passwd -U /etc/mosquitto/users.conf

echo "---> Generating necessary directories..."
mkdir -p /etc/mosquitto/ca_certificates
mkdir -p /etc/mosquitto/certs
mkdir -p /etc/mosquitto/conf.d

echo "---> Passing certificates..."
cp ./certs/ca.crt /etc/mosquitto/ca_certificates/ca.crt
cp ./certs/broker.key /etc/mosquitto/certs/broker.key
cp ./certs/broker.crt /etc/mosquitto/certs/broker.crt

echo "---> Changing ownership and permissions for new files and directories..."
chown -R mosquitto:mosquitto /etc/mosquitto
chmod 755 /etc/mosquitto
chmod 755 /etc/mosquitto/certs
chmod 755 /etc/mosquitto/ca_certificatres
chmod 644 /etc/mosquitto/*.conf
chmod 640 /etc/mosquitto/users.conf
chmod 640 /etc/mosquitto/ca_certificates/ca.crt
chmod 640 /etc/mosquitto/certs/broker.key
chmod 640 /etc/mosquitto/certs/broker.crt

echo "---> Generating configuration..."
touch /etc/mosquitto/mosquitto.conf
echo "password_file /etc/mosquitto/users.conf" > /etc/mosquitto/mosquitto.conf
echo "listener 8883 $1" >> /etc/mosquitto/mosquitto.conf
echo "allow_anonymous false" >> /etc/mosquitto/mosquitto.conf
echo "cafile /etc/mosquitto/ca_certificates/ca.crt" >> /etc/mosquitto/mosquitto.conf
echo "keyfile /etc/mosquitto/certs/broker.key" >> /etc/mosquitto/mosquitto.conf
echo "certfile /etc/mosquitto/certs/broker.crt" >> /etc/mosquitto/mosquitto.conf
echo "tls_version tlsv1.2" >> /etc/mosquitto/mosquitto.conf

echo "---> DONE"