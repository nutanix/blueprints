#!/bin/bash
set -ex

# -*- Variables and constants.
NETBOX_URL="@@{NETBOX_URL}@@"
VERSION=$(NETBOX_URL=${NETBOX_URL%.tar.gz} && echo "${NETBOX_URL##*/v}")
NETBOX_DNS="@@{NETBOX_DNS}@@"
NETBOX_USERNAME="@@{NETBOX_USERNAME}@@"
NETBOX_PASSWORD="@@{NETBOX_PASSWORD}@@"
NETBOX_PG_PASSWORD="@@{NETBOX_PG_PASSWORD}@@"

# -*- Installation and configure Netbox pre-requisites.
sudo yum update --quiet -y
sudo yum install -y --quiet epel-release
sudo yum install -y --quiet gcc python36 python36-devel python36-setuptools libxml2-devel libxslt-devel libffi-devel graphviz openssl-devel redhat-rpm-config nginx redis supervisor
sudo easy_install-3.6 pip
sudo /usr/local/bin/pip3 install gunicorn
sudo systemctl enable nginx supervisord redis
sudo systemctl stop nginx supervisord


# -*- Download and extract Netbox binaries
curl -C - -L -O --retry 6 --retry-max-time 60 --retry-delay 60 --silent --show-error $NETBOX_URL
sudo tar -zxvf v${VERSION}.tar.gz -C /opt
sudo ln -s /opt/netbox-${VERSION}/ /opt/netbox

cd /opt/netbox
sudo /usr/local/bin/pip3 install -q -r requirements.txt
sudo /usr/local/bin/pip3 install -q napalm django-rq

# -*- Create postgres users
sudo -i -u postgres psql -c 'CREATE DATABASE netbox;'
sudo -i -u postgres createuser -d -E -R -S netbox
sudo -i -u postgres psql -c "alter user netbox with encrypted password '${NETBOX_PG_PASSWORD}'; "
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox; "

# -*- Configure Netbox.
cd netbox/netbox/
sudo cp configuration.example.py configuration.py
sudo sed -i "s#ALLOWED_HOSTS = \[\]#ALLOWED_HOSTS = \['${NETBOX_DNS}', '@@{address}@@'\]#" configuration.py
sudo sed -i "s#    'USER': '',#    'USER': 'netbox',#" configuration.py
sudo sed -i "0,/PASSWORD/{s#    'PASSWORD': '',#    'PASSWORD': '${NETBOX_PG_PASSWORD}',#}" configuration.py
sudo sed -i '/SECRET_KEY/d' configuration.py
echo "SECRET_KEY = '$(../generate_secret_key.py)'" | sudo tee -a configuration.py
sudo sed -i 's/WEBHOOKS_ENABLED = False/WEBHOOKS_ENABLED = True/' configuration.py

cd /opt/netbox/netbox/
python3 manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('${NETBOX_USERNAME}', 'admin@example.com', '${NETBOX_PASSWORD}')" | python3 manage.py shell
sudo python3 manage.py collectstatic --no-input

# -*- Configure gunicorn.
echo "command = '/usr/local/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '127.0.0.1:8001'
workers = 3
user = 'nginx'" | sudo tee -a /opt/netbox/gunicorn_config.py

# -*- Configure supervisord.
echo "[program:netbox]
command = /usr/local/bin/gunicorn -c /opt/netbox/gunicorn_config.py netbox.wsgi
directory = /opt/netbox/netbox/
user = nginx

[program:netbox-rqworker]
command = python3 /opt/netbox/netbox/manage.py rqworker
directory = /opt/netbox/netbox/
user = nginx" | sudo tee -a /etc/supervisord.d/netbox.ini

# -*- Configure nginx.
echo "user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] \"\$request\" '
                      '\$status \$body_bytes_sent \"\$http_referer\" '
                      '\"\$http_user_agent\" \"\$http_x_forwarded_for\"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;
}" | sudo tee /etc/nginx/nginx.conf

echo "server{
    listen 80;

    server_name netbox.nutanix.com;

    client_max_body_size 25m;

    location /static/ {
        alias /opt/netbox/netbox/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        add_header P3P 'CP=\"ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV\"';
    }
}" | sudo tee -a /etc/nginx/conf.d/netbox.conf