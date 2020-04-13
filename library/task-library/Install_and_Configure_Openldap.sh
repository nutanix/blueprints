#!/bin/sh

#Variables used in this script
SECOND_LEVEL_DOMAIN_NAME="@@{SECOND_LEVEL_DOMAIN_NAME}@@"
TOP_LEVEL_DOMAIN_NAME="@@{TOP_LEVEL_DOMAIN_NAME}@@"
OPENLDAP_PASSWORD="@@{OPENLDAP_PASSWORD}@@"
CERTIFICATE_COUNTRY="@@{CERTIFICATE_COUNTRY}@@"
CERTIFICATE_STATE="@@{CERTIFICATE_STATE}@@"
CERTIFICATE_CITY="@@{CERTIFICATE_CITY}@@"

#Yum update and upgrade
sudo yum -y update
sudo yum -y upgrade

#Install required packages
sudo yum -y install net-tools bind-utils bash-completion nano firewalld
sudo echo "yum updates completed!" >> ~/status.txt

#Set hostname
sudo hostnamectl set-hostname openldap-host
sudo echo "hostname configured!" >> ~/status.txt

#Install openldap and required packages 
sudo yum -y install openldap compat-openldap openldap-clients openldap-servers openldap-servers-sql openldap-devel
sudo echo "openldap packages installed!" >> ~/status.txt

#Enable and start ldap service
sudo systemctl start slapd.service
sudo systemctl enable slapd.service
sudo echo "openldap services enabled and started!" >> ~/status.txt

sudo netstat -antup | grep -i 389 >> ~/status.txt
sudo echo "openldap status status - see above" >> ~/status.txt

#Install firewalld and enable and start the firewalld service
sudo yum -y install firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

#Firewall config
sudo firewall-cmd --permanent --add-service=ldap
sudo firewall-cmd --reload
sudo echo "firewall configured!" >> ~/status.txt
sudo sed -i -- 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

#OpenLdap configiration
sudo echo "dn: olcDatabase={2}hdb,cn=config
changetype: modify
replace: olcSuffix
olcSuffix: dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}

dn: olcDatabase={2}hdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}

dn: olcDatabase={2}hdb,cn=config
changetype: modify
replace: olcRootPW" | tee ~/db.ldif

sudo /usr/sbin/slappasswd -n -s ${OPENLDAP_PASSWORD} > ~/hash.txt

sudo echo "olcRootPW: `cat ~/hash.txt`" >> ~/db.ldif

sudo /usr/bin/ldapmodify -Y EXTERNAL  -H ldapi:/// -f ~/db.ldif

sudo echo "openldap configured!" >> ~/status.txt

sudo echo "dn: olcDatabase={1}monitor,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0}to * by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external, cn=auth" read by dn.base="cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}" read by * none
" | tee ~/monitor.ldif

sudo /usr/bin/ldapmodify -Y EXTERNAL  -H ldapi:/// -f ~/monitor.ldif

sudo echo "openldap restrict monitor access configured!" >> ~/status.txt

sudo /usr/bin/openssl req -new -x509 -subj "/C=${CERTIFICATE_COUNTRY}/ST=${CERTIFICATE_STATE}/L=${CERTIFICATE_CITY}/CN=${SECOND_LEVEL_DOMAIN_NAME}.${TOP_LEVEL_DOMAIN_NAME}" -nodes -out /etc/openldap/certs/${SECOND_LEVEL_DOMAIN_NAME}.pem -keyout /etc/openldap/certs/${SECOND_LEVEL_DOMAIN_NAME}.pem -days 365
chown -R ldap:ldap /etc/openldap/certs/*.pem
ll /etc/openldap/certs/*.pem >> ~/status.txt

sudo echo "certificate created!" >> ~/status.txt

sudo echo "dn: cn=config
changetype: modify
replace: olcTLSCertificateFile
olcTLSCertificateFile: /etc/openldap/certs/${SECOND_LEVEL_DOMAIN_NAME}.pem

dn: cn=config
changetype: modify
replace: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/openldap/certs/${SECOND_LEVEL_DOMAIN_NAME}.pem" | tee ~/certs.ldif

sudo /usr/bin/ldapmodify -Y EXTERNAL  -H ldapi:/// -f ~/certs.ldif

sudo echo "openldap secure communication configured!" >> ~/status.txt

sudo cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
sudo chown ldap:ldap /var/lib/ldap/*

sudo /usr/bin/ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/cosine.ldif
sudo /usr/bin/ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/nis.ldif 
sudo /usr/bin/ldapadd -Y EXTERNAL -H ldapi:/// -f /etc/openldap/schema/inetorgperson.ldif

sudo echo "dn: dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
dc: ${SECOND_LEVEL_DOMAIN_NAME}
objectClass: top
objectClass: domain

dn: cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
objectClass: organizationalRole
cn: ldapadm
description: LDAP Manager

dn: ou=People,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
objectClass: organizationalUnit
ou: People

dn: ou=Group,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
objectClass: organizationalUnit
ou: Group
" | tee ~/base.ldif

sudo /usr/bin/ldapadd -x -w ${OPENLDAP_PASSWORD} -D "cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}" -f ~/base.ldif

sudo echo "openldap database setup!" >> ~/status.txt

sudo echo "${TOP_LEVEL_DOMAIN_NAME}4.* /var/log/ldap.log" >> /etc/rsyslog.conf
sudo systemctl restart rsyslog

sudo echo "logging configured!" >> ~/status.txt
