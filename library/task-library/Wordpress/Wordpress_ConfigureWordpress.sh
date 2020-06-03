#!/bin/bash

#Get Wordpress installer
sudo setenforce 0
sudo sed -i 's/permissive/disabled/' /etc/sysconfig/selinux
wget http://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
sudo rsync -avP ~/wordpress/ /var/www/html/
sudo mkdir -p /var/www/html/wp-content/uploads
sudo chown -R apache:apache /var/www/html/*

#Configure WP
cd /var/www/html
cp wp-config-sample.php wp-config.php
sed -i '/DB_NAME/s/database_name_here/wordpress/g' wp-config.php
sed -i '/DB_USER/s/username_here/@@{WP_DB_USER}@@/g' wp-config.php
sed -i '/DB_PASSWORD/s/password_here/@@{WP_DB_PASSWORD}@@/g' wp-config.php
sed -i '/DB_HOST/s/localhost/@@{AZ_LIST(Entity(uuid="97412324-abb7-4cdf-99f9-ba18effec79b").get(Property("address")))}@@/g' wp-config.php

sudo systemctl restart httpd
