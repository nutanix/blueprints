#!/bin/bash

## Variable Initialization
VG_INFO="@@{VG_INFO}@@"  ### Its in format vgName|NoOfDisks in that VG e.g. "mongoData|3,mongoJournal|1,mongoLog|1"
PROFILE="@@{PROFILE}@@"  ### provider type e.g. "AZURE"

## Find out total disks attached to vm, total disk required for each volume group etc.
totalDisks=($(sudo lsblk -b -o NAME,SIZE,TYPE  | grep disk | awk '{print $1}' | sort ))
vgDisksCnt=($(echo ${VG_INFO} | sed 's/,.*|/,/g' |  sed 's/^.*|//' | tr "," " " ))
vgData=($(echo ${VG_INFO} | tr "," " " ))
totalDisksRequired=$(IFS=+; echo "$((${vgDisksCnt[*]}))")
unformattedDisks=()
vgDiskList=()

## Find out unformatted disks
for disk in ${totalDisks[@]}
do
    sudo fdisk -l /dev/${disk} 
    [[ $? -ne 0 ]] && continue
    cnt=`sudo fdisk  -l /dev/${disk} | grep "Device Boot" | wc -l `
    [[ $cnt -eq 0 ]] &&  unformattedDisks+=( "/dev/${disk}" )
done

## Check for unformatted disks should be more than required disks
errMsg="Insufficient unformattedDisks disks :  ${#unformattedDisks[@]} required is : ${totalDisksRequired} "
[[ ${totalDisksRequired} -gt ${#unformattedDisks[@]} ]] && echo ${errMsg[@]} && exit -1


if [[ "x${PROFILE}" == "xAZURE" ]]
then
    ## Get azure disks sorted in lun order
    ## TODO: Need to find more generic way to get all disks in order, 
    ##       though current case is more than sufficient for our case.
    sortedDisks=($(sudo ls -l /dev/disk/azure/scsi1/ | grep -v total | awk '{gsub("lun","",$9); gsub("../../../","",$11); print $11}'))
    azureDisks=()
    for disk in ${sortedDisks[@]}
    do 
        printf '%s\n' ${unformattedDisks[@]} | grep -q -P "^/dev/${disk}$"
        [[ $? -eq 0 ]] && azureDisks=( "${azureDisks[@]}" "/dev/${disk}" )
    done

    ## Get any disk if present, and which is not found in sorted disks.
    ## This is a fallback to make sure we should not missed any unformatted disks
    ## Ideally we should not get any disk from here.
    for disk in ${unformattedDisks[@]} 
    do 
        printf '%s\n' ${azureDisks[@]} | grep -q -P "^${disk}$" 
        [[ $? -eq 1 ]] && azureDisks=( "${azureDisks[@]}" "${disk}" )
    done
    vgDiskList=( "${azureDisks[@]}" )
else
    vgDiskList=( "${unformattedDisks[@]}" )
fi


offset=0
for vg in ${vgData[@]}
do
    vgName=`echo $vg |  cut -d'|' -f1`
    diskCnt=`echo $vg |  cut -d'|' -f2`

    vgDisks=("${vgDiskList[@]:$offset:$diskCnt}")
    offset=`expr $offset + $diskCnt`

    ## Do the LVM Setup for each volume group
    echo ${vgName}VG "${vgDisks[@]}"
    sudo pvcreate "${vgDisks[@]}"
    sudo vgcreate ${vgName}VG "${vgDisks[@]}"
    sudo lvcreate -l 100%FREE -i${diskCnt} -I1M -n ${vgName}LV ${vgName}VG 
    sudo lvchange -r 0 /dev/${vgName}VG/${vgName}LV
    sudo mkfs.xfs -K /dev/${vgName}VG/${vgName}LV
    sleep 1
done
