# ixnas-api

FreeNAS/TrueNAS scripts to help / hook into vm-bhyve for iSCSI creation. 


## Setup config
    cp config/ixnas-api.sample.ini config/ixnas-api.ini

Edit config, required [HOSTNAME], user= and password=

For iSCSI, iscsi_target_portalgroup= and iscsi_target_initiatorgroup= will be needed. 
    
## Usage

## create sparse zvol named testing6, for testing6.sjc1 Bhyve VM:

    python2.7 bin/create-zvol.py --host prodnas.ixsystems.com --vmname testing6.sjc1 --name "testing6" --size "20G" --sparse

## Create the complete iSCSI setup, 

This creates Targets, Extents and the Target-Extent association.  

     python2.7 bin/create-iscsi.py --host prodnas.ixsystems.com --vmname testing6.sjc1 --name "testing6"
     
The extent's serial number is also test to the target name, so that mappings can be done via names with geom DISKID:

    > glabel status
                                          Name  Status  Components
                          diskid/DISK-testing5     N/A  da0
                          diskid/DISK-testing6     N/A  da1

    > sudo iscsictl -A -p prodnas.ixsystems.com -t iqn.2005-08.com.ixsystems.sjc1:testing6
    > sudo iscsictl -L
    Target name                          Target portal    State
    iqn.2005-08.com.ixsystems.sjc1:testing5 prodnas.ixsystems.com Connected: da0
    iqn.2005-08.com.ixsystems.sjc1:testing6 prodnas.ixsystems.com Connected: da1

    > ls -l /dev/diskid/*
    crw-r-----  1 root  operator   0xfe Jan 19 01:44 /dev/diskid/DISK-testing5
    crw-r-----  1 root  operator  0x102 Jan 19 01:52 /dev/diskid/DISK-testing6

    
## UX

Not user friendly, will be back end call for vm-bhyve
    

    
    