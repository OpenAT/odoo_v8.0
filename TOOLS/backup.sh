#!/bin/bash

# Check free Space
typeset -i freespace
freespace=$(df -P DBBACKUPPATH | awk 'FNR>1{print $4}')

if [ ${freespace} -lt 1000000 ] ; then
    echo -e "ERROR: Backup apportet! Disk Space lower than 1GB!"
    exit 2
fi
TYPE=BACKUPTYPE
#%u   Tag der Woche (1..7); 1 steht für Montag
#%V   ISO‐Wochennummer mit Montag als erstem Tag der Woche (01..53)
WEEKDAY="`date +%u`"
WEEKNUMBER="`date +%V`"
if [ "${TYPE}" == "odoo-backup-zip" ] ; then
    if [ "${WEEKDAY}" == "7" ] ; then
        FILENAME=BACKUPFILE--week${WEEKNUMBER}.zip #="DBBACKUPPATH/DBNAME--week${WEEKNUMBER}.zip"
    else
        FILENAME=BACKUPFILE--day${WEEKDAY}.zip #="DBBACKUPPATH/DBNAME--day${WEEKDAY}.zip"
    fi
    INSTANCE_PATH/TOOLS/db-tools.py -b BASEPORT69 -s 'SUPER_PASSWORD' backup -d DBNAME -f ${FILENAME}
elif [ "${TYPE}" == "pad-backup-sql" ] ; then
    if [ "${WEEKDAY}" == "7" ] ; then
        FILENAME=BACKUPFILE--week${WEEKNUMBER}.sql #="DBBACKUPPATH/DBNAME--week${WEEKNUMBER}.zip"
    else
        FILENAME=BACKUPFILE--day${WEEKDAY}.sql #="DBBACKUPPATH/DBNAME--day${WEEKDAY}.zip"
    fi
    sudo -Hu postgres pg_dump DBNAME > ${FILENAME}
elif [ "${TYPE}" == "owncloud-backup-sql" ] ; then
    if [ "${WEEKDAY}" == "7" ] ; then
        FILENAME=BACKUPFILE--week${WEEKNUMBER}.sql #="/opt/odoo_v8.0/testodoo/o8_testodoo_backuptest11/BACKUP/o8_testodoo_backuptest11_cloud--week${WEEKNUMBER}.zip"
        DATAFILENAME=BACKUPFILE--week${WEEKNUMBER}-data
        CONFIGDATAFILENAME=BACKUPFILE--week${WEEKNUMBER}-config.tgz
    else
        FILENAME=BACKUPFILE--day${WEEKDAY}.sql #="/opt/odoo_v8.0/testodoo/o8_testodoo_backuptest11/BACKUP/o8_testodoo_backuptest11_cloud--day${WEEKDAY}.zip"
        DATAFILENAME=BACKUPFILE--day${WEEKDAY}-data
        CONFIGDATAFILENAME=BACKUPFILE--day${WEEKDAY}-config.tgz
    fi
    sudo -Hu postgres pg_dump DBNAME > ${FILENAME}
    rsync -avz DBPATH/owncloud/data/ ${DATAFILENAME}
    #tar -pzvf ${DATAFILENAME} /opt/odoo_v8.0/testodoo/o8_testodoo_backuptest11/owncloud/data
    tar -czvf ${CONFIGDATAFILENAME} DBPATH/owncloud/config/config.php
fi

#INSTANCE_PATH/TOOLS/db-tools.py -b BASEPORT69 -s 'SUPER_PASSWORD' backup -d DBNAME -f ${FILENAME}
# Todo: Create Backup directory
