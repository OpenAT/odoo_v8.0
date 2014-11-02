#!/bin/bash

# Check free Space
typeset -i freespace
freespace=$(df -P DBBACKUPPATH | awk 'FNR>1{print $4}')

if [ ${freespace} -lt 1000000 ] ; then
    echo -e "ERROR: Backup apportet! Disk Space lower than 1GB!"
    exit 2
fi

#%u   Tag der Woche (1..7); 1 steht für Montag
#%V   ISO‐Wochennummer mit Montag als erstem Tag der Woche (01..53)
WEEKDAY="`date +%u`"
WEEKNUMBER="`date +%V`"
if "${WEEKDAY}" == "7"; then
    BACKUPFILE="DBBACKUPPATH/DBNAME--week${WEEKNUMBER}.zip"
else
    BACKUPFILE="DBBACKUPPATH/DBNAME--day${WEEKDAY}.zip"
fi
INSTANCE_PATH/TOOLS/db-tools.py -b BASEPORT69 -s SUPER_PASSWORD backup -d DBNAME -f ${BACKUPFILE}

# Todo: Backup etherpad-lite database
# Todo: Backup owncloud database and data directory
