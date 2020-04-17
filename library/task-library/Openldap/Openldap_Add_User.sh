#!/bin/sh

#Variables used in this script 
ADMIN_USER="@@{ADMIN_USER}@@"
ADMIN_PASSWORD="@@{ADMIN_PASSWORD}@@"
READONLY_USER="@@{READONLY_USER}@@"
READONLY_PASSWORD="@@{READONLY_PASSWORD}@@"
OPENLDAP_PASSWORD="@@{OPENLDAP_PASSWORD}@@"
SECOND_LEVEL_DOMAIN_NAME="@@{SECOND_LEVEL_DOMAIN_NAME}@@"
TOP_LEVEL_DOMAIN_NAME="@@{TOP_LEVEL_DOMAIN_NAME}@@"


# Test openldap configuration
sudo /usr/sbin/slaptest -u >> ~/status.txt
sudo echo "look for 'config file testing succeeded' above" >> ~/status.txt
sudo echo "openldap configuration completed!" >> ~/status.txt

# create the built-in users
sudo echo "dn: uid=${ADMIN_USER},ou=People,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
objectClass: top
objectClass: account
objectClass: posixAccount
objectClass: shadowAccount
cn: ${ADMIN_USER}
uid: ${ADMIN_USER}
uidNumber: 1021
gidNumber: 101
homeDirectory: /home/${ADMIN_USER}
loginShell: /bin/bash
gecos: OpenLDAP Administrator
userPassword: ${ADMIN_PASSWORD}
shadowLastChange: 17023
shadowMin: 0
shadowMax: 99999
shadowWarning: 7

dn: uid=${READONLY_USER},ou=People,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
objectClass: top
objectClass: account
objectClass: posixAccount
objectClass: shadowAccount
cn: ${READONLY_USER}
uid: ${READONLY_USER}
uidNumber: 2022
gidNumber: 102
homeDirectory: /home/${READONLY_USER}
loginShell: /bin/bash
gecos: Cluster View Only user
userPassword: ${READONLY_PASSWORD}
shadowLastChange: 17023
shadowMin: 0
shadowMax: 99999
shadowWarning: 7" | tee ~/builtInUsers.ldif

# create the built-in groups
sudo echo "dn: cn=ClusterAdmin,ou=Group,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
cn: ClusterAdmin
objectClass: top
objectClass: posixGroup
gidNumber: 101
memberUid: ${ADMIN_USER}

dn: cn=Viewer,ou=Group,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}
cn: Viewer
objectClass: top
objectClass: posixGroup
gidNumber: 102
memberUid: ${READONLY_USER}" | tee ~/builtInGroups.ldif

sudo /usr/bin/ldapadd -x -w ${OPENLDAP_PASSWORD} -D "cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}" -f ~/builtInUsers.ldif
sudo /usr/bin/ldapadd -x -w ${OPENLDAP_PASSWORD} -D "cn=ldapadm,dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME}" -f ~/builtInGroups.ldif

# verify the new user was added
sudo ldapsearch -x cn=${ADMIN_USER} -b dc=${SECOND_LEVEL_DOMAIN_NAME},dc=${TOP_LEVEL_DOMAIN_NAME} >> ~/status.txt

