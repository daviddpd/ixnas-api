# ixnas-api

FreeNAS/TrueNAS scripts to help / hook into vm-bhyve for iSCSI creation. 


## Setup config
    cp config/ixnas-api.sample.ini config/ixnas-api.ini

Edit config, required [HOSTNAME], user= and password=
    
## Usage

    python2.7 bin/create-zvol.py --host nas1.iad1.ixsystems.com --vmname testing2.sjc1 --name "testing3" --size "20G" --sparse
    
## UX

Not user friendly, will be back end call for vm-bhyve
    

    
    