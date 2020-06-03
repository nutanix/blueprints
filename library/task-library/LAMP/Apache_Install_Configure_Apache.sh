#!/bin/bash
set -ex

## -*- Install httpd and php
sudo yum update -y
sudo yum -y install epel-release
sudo rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
sudo yum install -y httpd php56w php56w-mysql

## Configure php module in apache
echo "<IfModule mod_dir.c>
        DirectoryIndex index.php index.html index.cgi index.pl index.php index.xhtml index.htm
</IfModule>" | sudo tee /etc/httpd/conf.modules.d/dir.conf

echo "<?php
phpinfo();
?>" | sudo tee /var/www/html/info.php 

## Restart apache service
sudo systemctl restart httpd
sudo systemctl enable httpd