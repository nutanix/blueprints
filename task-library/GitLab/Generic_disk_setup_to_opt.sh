#!/bin/bash
set -ex

##############################################
# Name        : Generic_disk_setup_to_opt.sh
# Author      : Calm Devops
# Version     : 1.0
# Description : Script is used to group all possible disk to single group and create one logical volume of that
# Compatibility : Centos 6, 7
##############################################

sudo yum update -y --quiet
sudo yum install -y --quiet lvm2 libudev-devel
pv_list=""		# This variable will store all the unused/unclaimed disks 
for x in {a..z}; do
   if [ -e /dev/sd$x ];	# For all providers except AWS
   then
      data_flag=`sudo file -sL /dev/sd$x | cut -d ':' -f2 | tr -d ' '`	# It will be 'data' if disk is not claimed / used
      if [ "$data_flag" == "data" ]
      then
      sudo pvcreate /dev/sd$x
      pv_list+="/dev/sd$x "
      fi
   elif [ -e /dev/xvd$x ];	# AWS disks
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
	eval sudo vgcreate vg01 $pv_list # vg01 is created with all unclaimed / unused disks
    sudo lvcreate -l 100%VG -n lv01 vg01	# lv01 is created from vg01 
	sudo mkfs.xfs /dev/vg01/lv01
	echo -e "/dev/vg01/lv01 \t /opt \t xfs \t defaults \t 0 0" | sudo tee -a /etc/fstab # lv01 is mounted to /opt
	sudo mount -a
fi
