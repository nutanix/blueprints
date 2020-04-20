#!/bin/bash
set -ex

##############################################
# Name        : Generic_disk_setup.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to group all possible disk to single group and create one logical volume of that
# Compatibility : Centos 6, 7
##############################################

sudo yum update -y --quiet
sudo yum install -y --quiet lvm2 libudev-devel
pv_list=""			# This variable will store all the unused or unclaimed disks 
for x in {a..z}; do
   if [ -e /dev/sd$x ];		# For all providers except AWS
   then
      data_flag=`sudo file -sL /dev/sd$x | cut -d ':' -f2 | tr -d ' '`
      if [ "$data_flag" == "data" ]
      then
      sudo pvcreate /dev/sd$x
      pv_list+="/dev/sd$x "
      fi
   elif [ -e /dev/xvd$x ];	#AWS disks
   then
      data_flag=`sudo file -sL /dev/xvd$x | cut -d ':' -f2 | tr -d ' '`
      if [ "$data_flag" == "data" ]
      then
        sudo pvcreate /dev/xvd$x
        pv_list+="/dev/xvd$x "
      fi
   fi
done

if [[ ! -z $pv_list ]]; then
	eval sudo vgcreate vg01 $pv_list	# vg01 is created with all unclaimed or unused disks
    sudo lvcreate -l 100%VG -n lv01 vg01	# lv01 is created from vg01
	sudo mkfs.xfs /dev/vg01/lv01
    sudo mkdir -p @@{MOUNT_PATH}@@
	echo -e "/dev/vg01/lv01 \t @@{MOUNT_PATH}@@ \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab	# lv01 is mounted to @@{MOUNT_PATH}@@
	sudo mount -a
fi


