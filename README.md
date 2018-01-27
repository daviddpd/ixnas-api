# ixnas-api

FreeNAS/TrueNAS scripts to help / hook into vm-bhyve for iSCSI creation. 


## Setup config
    cp config/ixnas-api.sample.ini config/ixnas-api.ini

Ideally, maybe better to do this, for a global host config:
    sudo mkdir -p /usr/local/etc/ixnas-api/config
    cp config/ixnas-api.sample.ini /usr/local/etc/ixnas-api/config/ixnas-api.ini

Edit config, required [HOSTNAME], user= and password=,  The HOSTNAME is whatever you'll be using on the command line, 
so if using short, non-FQDN, then use those in the config.

For iSCSI, iscsi_target_portalgroup= and iscsi_target_initiatorgroup= will be needed.  You need to set these up manually in the
FreeNAS/TrueNAS UI.  Most likely, they will both simply be the number 1.
  
## Usage

## create sparse zvol named testing10.iad1, for testing10.iad1 Bhyve VM:

    > bin/create-zvol.py --host nas1 --vmname testing10.iad1 --name "testing10.iad1" --size "20G" --sparse

## Create the complete iSCSI setup, 

This creates Targets, Extents and the Target-Extent association.  

    > bin/create-iscsi.py --host nas1 --vmname testing10.iad1 --name "testing10.iad1"
     
Due to a 16 byte length limit for the extent's serial number, if the --diskserial is past, it is set that that, otherwise
a UUID is generated, and the default string is built in the form of "${time_low}-${time_mid}-00".


    > sudo iscsictl -A -p nas1 -t iqn.2005-08.com.ixsystems.iad1:testing10.iad1

    > sudo iscsictl -L

        Target name                          Target portal    State
        iqn.2005-08.com.ixsystems.iad1:testing10.iad1 nas1             Connected: da0

    > glabel status
                                      Name  Status  Components                                      
               diskid/DISK-a09bb06e-2fe-00     N/A  da0

    > ls -l /dev/diskid/
        total 0
        crw-r-----  1 root  operator  0x94 Jan 27 01:13 DISK-a09bb06e-2fe-00

## UX

Things should be non-verbose by default, and should bail out and exit with rc=1 if a problem happens.    

    
    