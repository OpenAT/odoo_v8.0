#!/bin/bash
#######################################################################################################################

GITPATH="https://github.com/OpenAT"
REPONAME="odoo_v8.0"
SOURCE_REPO=${GITPATH}/${REPONAME}.git

GITRAW="https://raw.githubusercontent.com/OpenAT/${REPONAME}/master"

SCRIPT_MODE=$1

# ---------------------------------------------------------
# SCRIPT START
# ---------------------------------------------------------
echo -e "\n===== SCRIPT START odoo-tools.sh ====="

# ----- Set Script Path:
# "/home/user/bin/foo.sh"
SCRIPT=$(readlink -f "$0")
# "/home/user/bin"
SCRIPTPATH=$(cd ${0%/*} && pwd -P)

# ----- Check UBUNTU Version:
source /etc/lsb-release
if [ $DISTRIB_ID = "Ubuntu" ] && [ $DISTRIB_RELEASE = "14.04" ] ; then
    echo -e "OS Version: $DISTRIB_ID $DISTRIB_RELEASE"
else
    echo -e "ERROR: This Script only works on Ubuntu 14.04!"; exit 2
fi

# ----- Check script is started as root:
if [ "$EUID" -ne 0 ]; then
    echo -e "ERROR: Please run as root!"; exit 2
fi

# ----- Repo Path for all odoo instances:
REPOPATH="/opt/${REPONAME}"
if [ -d ${REPOPATH} ]; then
    echo -e "Directory ${REPOPATH} exists."
else
    if  mkdir ${REPOPATH} 2>&1>/dev/null; then
	    echo -e "Created directory ${REPOPATH}"
    else
        echo -e "ERROR: Could not create directory ${REPOPATH}!"; exit 2
    fi
fi
chmod 755 ${REPOPATH}

# ----- Repo SETUP Path for all odoo instances:
REPO_SETUPPATH="${REPOPATH}/SETUP"
if [ -d ${REPO_SETUPPATH} ]; then
    echo -e "Directory ${REPO_SETUPPATH} exists."
else
    if  mkdir ${REPO_SETUPPATH} 2>&1>/dev/null; then
	    echo -e "Created directory ${REPO_SETUPPATH}"
    else
        echo -e "ERROR: Could not create directory ${REPO_SETUPPATH}!"; exit 2
    fi
fi
chmod 755 ${REPOPATH}


# ---------------------------------------------------------
# $ odoo-tools.sh PREPARE
# ---------------------------------------------------------
if [ "$SCRIPT_MODE" = "prepare" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh prepare"
    echo -e "-----------------------------------------------------------------------"
    if [ $# -ne 1 ]; then
        echo -e "ERROR: \"setup-toosl.sh prepare\" takes exactly one argument!"; exit 2
    fi
    cd ${REPO_SETUPPATH}

    # ----- Prepare LOG-File:
    SETUP_LOG="${REPO_SETUPPATH}/prepare--`date +%Y-%m-%d__%H-%M`.log"
    if [ -w "$SETUP_LOG" ] ; then
        echo -e "Setup log file: ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
    else
        if  touch $SETUP_LOG 2>&1>/dev/null; then
            echo -e "Setup log file ist at ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
        else
            echo -e "ERROR: Could not create log file ${SETUP_LOG}!"; exit 2
        fi
    fi

    # ----- Check locale settings:
    locale_set=false
    if ! [ -e "/etc/default/locale" ]; then
        touch /etc/default/locale
        locale_set=true
    fi

    if ! egrep -i "LANG=.*UTF-8" /etc/default/locale >> $SETUP_LOG; then
        echo 'LANG="en_US.UTF-8"' >> /etc/default/locale
        locale_set=true
    fi

    if ! egrep -i "LANGUAGE=...+" /etc/default/locale >> $SETUP_LOG; then
        echo 'LANGUAGE="en_US.UTF-8"' >> /etc/default/locale
        locale_set=true
    fi
    locale-gen en_US.UTF-8 >> $SETUP_LOG
    locale-gen de_AT.UTF-8 >> $SETUP_LOG
    update-locale >> $SETUP_LOG
    if [ "$locale_set" = true ]; then
        echo "ERROR: Wrong locale settings (NOT UTF8)! Please logout completely, login and try again!"
        exit 3
    fi

    # ----- Update Server
    echo -e "\n----- Update Server"
    apt-get upgrade -y >> $SETUP_LOG
    apt-get update >> $SETUP_LOG
    echo -e "----- Update Server Done"

    # ----- Install Basic Packages
    echo -e "\n----- Install Basic Packages"
    apt-get install ssh wget sed git git-core gzip curl python libssl-dev libxml2-dev libxslt-dev build-essential \
        gcc mc bzr lptools make nodejs -y >> $SETUP_LOG
    echo -e "----- Install Basic Packages Done"

    # ----- Install postgresql
    echo -e "\n----- Install postgresql"
    apt-get install postgresql postgresql-server-dev-9.3 libpq-dev -y >> $SETUP_LOG
    update-rc.d postgresql defaults >> $SETUP_LOG
    service postgresql restart | tee -a $SETUP_LOG
    echo -e "----- Install postgresql Done"

    # ----- Install nginx
    echo -e "\n----- Install nginx"
    apt-get remove apache2 apache2-mpm-event apache2-mpm-prefork apache2-mpm-worker -y >> $SETUP_LOG
    apt-get install nginx -y >> $SETUP_LOG
    update-rc.d nginx defaults >> $SETUP_LOG
    service nginx restart | tee -a $SETUP_LOG
    echo -e "----- Install nginx Done"

    # ----- Install Python Packages
    echo -e "\n----- Install Python Apt Packages"
    apt-get install python-pip python-virtualenv python-dev python-software-properties python-pychart \
        python-genshi python-pyhyphen python-ldap -y >> $SETUP_LOG
    pip install pyserial >> $SETUP_LOG
    pip install qrcode >> $SETUP_LOG
    pip install --pre pyusb >> $SETUP_LOG
    echo -e "\n----- Install Python Apt Packages DONE"

    # ----- Install Wkhtmltopdf 0.12.1
    echo -e "\n----- Install Wkhtmltopdf 0.12.1"
    if wkhtmltopdf -V | grep "wkhtmltopdf.*12.*" 2>&1>/dev/null; then
      echo -e "\nWkhtmltopdf 0.12.1 seems to be installed! Skipping installation!\n"
    else
        apt-get install libjpeg-dev libjpeg8-dev libtiff5-dev vflib3-dev pngtools libpng3 -y >> $SETUP_LOG
        apt-get install xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic -y >> $SETUP_LOG
        ## curl -L to follow mirror redirect from sourceforge.net (eg. kaz.sourceforge.net...)
        cd ${REPO_SETUPPATH}
        wget http://kaz.dl.sourceforge.net/project/wkhtmltopdf/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb >> $SETUP_LOG
        dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb >> $SETUP_LOG
        cp /usr/local/bin/wkhtmltopdf /usr/bin >> $SETUP_LOG
        cp /usr/local/bin/wkhtmltoimage /usr/bin >> $SETUP_LOG
        apt-get install flashplugin-nonfree -y >> $SETUP_LOG
        pip install git+https://github.com/qoda/python-wkhtmltopdf.git >> $SETUP_LOG
    fi
    echo -e "\n----- Install Wkhtmltopdf 0.12.1 DONE"

    # ----- Install python libs from requirements.txt
    echo -e "\n----- Install python libs from requirements.txt"
    wget -O - ${GITRAW}/TOOLS/requirements.txt | grep -v '.*#' > ${REPO_SETUPPATH}/requirements.txt
    while read line; do
        if pip install ${line} >> $SETUP_LOG; then
            echo -e "Installed: ${line}"
        else
            echo -e "\n\nWARNING Install FAILED: ${line} !\n\n" | tee -a $SETUP_LOG
        fi
        if pip freeze | grep ${line} >> $SETUP_LOG; then
            echo -e "PackageOK: ${line} "
        else
            echo -e "\n\nWARNING: Package ${line} missing!\n\n" | tee -a $SETUP_LOG
        fi
    done < ${REPO_SETUPPATH}/requirements.txt
    echo -e "----- Install python libs from requirements.txt Done"

    # ----- Install Packages for AerooReports
    echo -e "\n----- Install Packages for AerooReports"
    # ATTENTION: LibreOffice-Python 2.7 Compatibility Script Author: Holger Brunn (https://gist.github.com/hbrunn/6f4a007a6ff7f75c0f8b)
    # Maybe this is needed because of python-uno bridge?!? - We will see when we start the test for aeroo reports in v8
    easy_install uno
    apt-get install ure uno-libs3 unoconv graphviz ghostscript\
                    libreoffice-core libreoffice-common libreoffice-base libreoffice-base-core \
                    libreoffice-draw libreoffice-calc libreoffice-writer libreoffice-impress \
                    python-cupshelpers hyphen-de hyphen-en-us -y >> $SETUP_LOG
    echo -e "\nInstall Aeroolib"
    if pip freeze | grep aeroolib ; then
        echo -e "\n\nWARNING: Aeroolib seems to be already installed!" | tee -a $SETUP_LOG
        echo -e "Please upgrade manually if needed!"
        echo -e "Aeroolib has to be at least aeroolib==1.2.0 to work with ${REPONAME}\n\n"
    else
        if [ -d ${REPO_SETUPPATH}/aeroolib ]; then
            echo -e "Do not clone aeroolib from github since directory ${REPO_SETUPPATH}/aeroolib exists ."
        else
            echo -e "Clone aeroolib from github."
            # TODO: Use our aeroolib from odoo_v8.0
            git clone --depth 1 --single-branch https://github.com/aeroo/aeroolib.git ${REPO_SETUPPATH}/aeroolib >> $SETUP_LOG
        fi
        cd ${REPO_SETUPPATH}/aeroolib >> $SETUP_LOG
        python ${REPO_SETUPPATH}/aeroolib/aeroolib/setup.py install | tee -a $SETUP_LOG
        cd ${REPO_SETUPPATH} >> $SETUP_LOG
        echo -e "\nInstall Aeroo LibreOffice Service to init.d as service aeroo"
        wget -O - https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/TOOLS/aeroo.init > ${REPO_SETUPPATH}/aeroo.init
        chmod ugo=rx ${REPO_SETUPPATH}/aeroo.init >> $SETUP_LOG
        ln -s ${REPO_SETUPPATH}/aeroo.init /etc/init.d/aeroo >> $SETUP_LOG
        update-rc.d aeroo defaults >> $SETUP_LOG
        service aeroo stop
        service aeroo start
    fi
    echo -e "----- Install Packages for AerooReports Done"

    # ----- Install Packages for Etherpad Lite
    echo -e "\n----- Install Packages for Etherpad Lite"
    apt-get install abiword -y >> $SETUP_LOG
    echo -e "----- Install Packages for Etherpad Lite Done"

    # ----- Install npm and Less compiler needed by Odoo 8 Website - added from https://gist.github.com/rm-jamotion/d61bc6525f5b76245b50
    echo -e "----- Install npm (requires nodejs) and less compiler"
    curl -L https://npmjs.org/install.sh | sh >> $SETUP_LOG
    npm install less >> $SETUP_LOG
    echo -e "----- Install nodejs and less compiler DONE"

    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh prepare DONE"
    echo -e "-----------------------------------------------------------------------"
    echo -e "\n!!!PLEASE REBOOT THIS SERVER NOW!!!\n"
    exit 0
fi


# -----------------------------------------------------------------------
# $ odoo-tools.sh setup {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}
# -----------------------------------------------------------------------
if [ "$SCRIPT_MODE" = "setup" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh setup {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}"
    echo -e "-----------------------------------------------------------------------"
    echo -e "You have to run \"odoo-tools.sh prepare\" before setting up your first instance!\n"
    if [ $# -ne 4 ]; then
        echo -e "ERROR: \"setup-toosl.sh prepare\" takes exactly four arguments!"
        exit 2
    fi

    # ----- Set CMD Variables
    TARGET_BRANCH=$2
    SUPER_PASSWORD=$3
    DOMAIN_NAME=$4

    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"
    
    # ----- Check if the TARGET_BRANCH already exists
    if git ls-remote ${SOURCE_REPO} | grep -sw "${TARGET_BRANCH}" 2>&1>/dev/null; then
        echo "ERROR: ${TARGET_BRANCH} already exists in ${REPONAME}!"; exit 2
    fi    

    # ----- Create Instance Log File for SETUP
    INSTANCE_SETUPLOG="${REPO_SETUPPATH}/setup--${TARGET_BRANCH}--`date +%Y-%m-%d__%H-%M`.log"
    if [ -w "${INSTANCE_SETUPLOG}" ] ; then
        echo -e "ERROR: ${INSTANCE_SETUPLOG} already exists!"
        exit 2
    else
        if  touch ${INSTANCE_SETUPLOG} 2>&1>/dev/null; then
            echo -e "Setup log ${INSTANCE_SETUPLOG} created. (Use tail -f ${INSTANCE_SETUPLOG} during install.)"
        else
            echo -e "ERROR: Could not create log file ${INSTANCE_SETUPLOG}!"
            exit 2
        fi
    fi

    # ----- Prepare Log Directory and Variable
    INSTANCE_LOGPATH="/var/log/${REPONAME}_${TARGET_BRANCH}"
    INSTANCE_LOGFILE="${INSTANCE_LOGPATH}/${TARGET_BRANCH}.log"
    if [ -d "${INSTANCE_LOGPATH}" ] ; then
        echo -e "ERROR: ${INSTANCE_LOGPATH} already exists!"
        exit 2
    else
        if  mkdir ${INSTANCE_LOGPATH} 2>&1>/dev/null; then
            echo -e "Log Directory ${INSTANCE_LOGPATH} created."
        else
            echo -e "ERROR: Could not create log directory ${INSTANCE_LOGPATH}!"
            exit 2
        fi
    fi
    chown ${DBUSER}:${DBUSER} ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG
    chmod ug=rw ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG
    chmod o=r ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG

    # ---- Set BASEPORT
    COUNTERFILE=${REPO_SETUPPATH}/${REPONAME}.counter
    if [ -f ${COUNTERFILE} ]; then
        echo -e "File ${COUNTERFILE} exists."
    else
        if  touch ${COUNTERFILE} 2>&1>/dev/null; then
            # Port Schema for odoo [0][00][00]
            # [0]=Odoo_Version_Start [00-99]=Local_Instances [00-99]=Instance_Services
            #
            # [0] = Odoo Versions:
            #       4 = odoo OLD setups 6or7 old install
            #       1 = odoo 8 (=99 Instancen pro Server) e.g.: 10069 or 12369
            #       2 = odoo 9
            #       3 = odoo 10 usw e.g.: 30069
            #
            # Highest Linux Port Number (2^16)-1, or 0-65,535 (the -1 is because port 0 is reserved and unavailable)
            echo -e "10" > ${COUNTERFILE};
            echo -e "File ${COUNTERFILE} created."
        else
            echo -e "ERROR: Could not create file ${COUNTERFILE}!"
            exit 2
        fi
    fi
    typeset -i BASEPORT
    BASEPORT=`cat ${COUNTERFILE}`+1
    if [ ${BASEPORT} -lt 10 ]; then
        echo echo -e "ERROR: Could not Update ${BASEPORT}!"
        exit 2
    fi
    echo $BASEPORT > ${COUNTERFILE}

    # ----- Basic Variables
    DBUSER="${TARGET_BRANCH}"
    DBPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`
    ETHERPADKEY=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 16 | head -1`

    # ----- Allow the user to check all arguments:
    echo -e ""
    echo -e "\$1 Script Mode                    :  $SCRIPT_MODE" | tee -a $INSTANCE_SETUPLOG
    echo -e "\$2 Target Branch                  :  $TARGET_BRANCH" | tee -a $INSTANCE_SETUPLOG
    echo -e "\$3 Super Password                 :  $SUPER_PASSWORD" | tee -a $INSTANCE_SETUPLOG
    echo -e "\$4 Domain Name                    :  $DOMAIN_NAME" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Instance Setuplog File            :  $INSTANCE_SETUPLOG" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Instance Instance Name            :  $TARGET_BRANCH" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Base Directory           :  $INSTANCE_PATH" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Logfile                  :  $INSTANCE_LOGFILE" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Baseport                 :  $BASEPORT" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Database User Name       :  $DBUSER" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Database User Password   :  $DBPW" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance LINUX User               :  $DBUSER" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Etherpad SESSION KEY     :  $ETHERPADKEY" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Would you like to setup a new odoo instance with this settings? ( Y/N ): "; read answer
    if [ "${answer}" != "Y" ]; then
        while [ "${answer}" != "Y" ]; do
            if [ "${answer}" == "n" ] || [ "${answer}" == "N" ]; then
                echo "SETUP APPORTED: EXITING SCRIPT!"
                rm ${INSTANCE_SETUPLOG}
                rm -r ${INSTANCE_PATH}
                rm -r ${INSTANCE_LOGPATH}
                exit 1
            fi
            echo "Please enter Y (Yes) or N (No)"; read answer
        done
    fi

    # ----- Clone the Github Repo (Directory created here first!)
    echo -e "\n---- Clone the Github Repo ${REPONAME}"
    git clone -b master --recurse-submodules \
        ${SOURCE_REPO} ${INSTANCE_PATH} | tee -a $INSTANCE_SETUPLOG
    cd ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG
    git branch ${TARGET_BRANCH} >> $INSTANCE_SETUPLOG
    git checkout ${TARGET_BRANCH} >> $INSTANCE_SETUPLOG
    if [ ! -d "${INSTANCE_PATH}/odoo/addons" ]; then
        echo -e "\nERROR: Cloning the github repo failed!\n"; exit 2
    fi


    # ----- ToDo virtualenv environment for our new instance
    #virtualenv ${INSTANCE_PATH}/VIRTUALENV
    #source ${INSTANCE_PATH}/VIRTUALENV/bin/activate
    #pip install --upgrade pip
    #pip install --upgrade virtualenv
    #hash -r
    #which pip
    #
    # DO ALL THE PACKAGE INSTALL LIKE IN PREPARE
    #
    # http://stackoverflow.com/questions/16237490/i-screwed-up-the-system-version-of-python-pip-on-ubuntu-12-10
    # https://www.digitalocean.com/community/tutorials/common-python-tools-using-virtualenv-installing-with-pip-and-managing-packages
    # http://wiki.ubuntuusers.de/virtualenv


    # ----- Setup the Linux User and Group
    echo -e "\n----- Create Instance Linux User and Group: ${DBUSER}"
    useradd -m -s /bin/bash ${DBUSER} | tee -a $INSTANCE_SETUPLOG

    # ----- Set correct Rights
    chown -R ${DBUSER}:${DBUSER} ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG
    chmod 755 ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG
    chown -R ${DBUSER}:${DBUSER} ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG
    chmod 755 ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG

    # ----- Create Database User
    echo -e "\n---- Create postgresql role $DBUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${DBUSER}' WITH NOSUPERUSER CREATEDB LOGIN PASSWORD '\'${DBPW}\''"' | tee -a $INSTANCE_SETUPLOG

    # ----- Create server.conf
    echo -e "\n---- Create odoo server config in: ${INSTANCE_PATH}/${TARGET_BRANCH}.conf"
    /bin/sed '{
        s!'"addons_path = odoo/openerp/addons,odoo/addons,addons-loaded"'!'"addons_path = ${INSTANCE_PATH}/odoo/openerp/addons,${INSTANCE_PATH}/odoo/addons,${INSTANCE_PATH}/addons-loaded"'!g
        s!'"admin_passwd = admin"'!'"admin_passwd = ${SUPER_PASSWORD}"'!g
        s!'"data_dir = data_dir"'!'"data_dir = ${INSTANCE_PATH}/data_dir"'!g
        s!'"db_password = odoo"'!'"db_password = ${DBPW}"'!g
        s!'"db_user = odoo"'!'"db_user = ${DBUSER}"'!g
        s!'"logfile = None"'!'"logfile = ${INSTANCE_LOGFILE}"'!g
        s!'"logrotate = False"'!'"logrotate = True"'!g
        s!'"longpolling_port = 8072"'!'"longpolling_port = ${BASEPORT}72"'!g
        s!'"xmlrpc_port = 8069"'!'"xmlrpc_port = ${BASEPORT}69"'!g
        s!'"xmlrpcs_port = 8071"'!'"xmlrpcs_port = ${BASEPORT}71"'!g
            }' ${INSTANCE_PATH}/TOOLS/server.conf > ${INSTANCE_PATH}/${TARGET_BRANCH}.conf | tee -a $INSTANCE_SETUPLOG
    chown root:root ${INSTANCE_PATH}/${TARGET_BRANCH}.conf
    chmod ugo=r ${INSTANCE_PATH}/${TARGET_BRANCH}.conf

    # ----- Create the Init Script for odoo
    echo -e "\n---- Setup init.d for instance: ${INSTANCE_PATH}/${TARGET_BRANCH}.init"
    /bin/sed '{
        s,DBUSER,'"$DBUSER"',g
        s,TARGET_BRANCH,'"$TARGET_BRANCH"',g
        s,INSTANCE_PATH,'"$INSTANCE_PATH"',g
            }' ${INSTANCE_PATH}/TOOLS/server.init > ${INSTANCE_PATH}/${TARGET_BRANCH}.init | tee -a $INSTANCE_SETUPLOG
    chown root:root ${INSTANCE_PATH}/${TARGET_BRANCH}.init
    chmod ugo=rx ${INSTANCE_PATH}/${TARGET_BRANCH}.init
    ln -s ${INSTANCE_PATH}/${TARGET_BRANCH}.init /etc/init.d/${TARGET_BRANCH} | tee -a $INSTANCE_SETUPLOG
    update-rc.d ${TARGET_BRANCH} defaults | tee -a $INSTANCE_SETUPLOG
    service ${TARGET_BRANCH} start | tee -a $INSTANCE_SETUPLOG

    # ----- Link Log Path if logfile exists (should be there after first start!)
    if [ -s ${INSTANCE_LOGFILE} ]; then
        ln -s ${INSTANCE_LOGPATH} ${INSTANCE_PATH}/LOG
    else
        echo -e "\n\n----------\nWARNING: Log file for instance was NOT created!\n----------\n\n" | tee -a $INSTANCE_SETUPLOG
    fi


    # ----- Setup nginx # INFO Maybe check the proxy setting from v7 because of nginx ;)

    # ----- Setup Etherpad-Lite
    # ----- Setup cron Logrotate for all Logfiles
    # ----- Setup cron backup script

    # Maybe: Test URL to database - should work with v8.0
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh setup {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME} DONE"
    echo -e "-----------------------------------------------------------------------"
    exit 0
fi


# ---------------------------------------------------------
# Script HELP
# ---------------------------------------------------------
echo -e "\n----- SCRIPT USAGE -----"
echo -e "$ odoo-tools.sh {prepare|setup|deploy|backup|restore} ...\n"
echo -e "$ odoo-tools.sh prepare"
echo -e "$ odoo-tools.sh setup   {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}"
echo -e "TODO: $ odoo-tools.sh update  {TARGET_BRANCH}"
echo -e "TODO: $ odoo-tools.sh deploy  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "TODO: $ odoo-tools.sh backup  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all}"
echo -e "TODO: $ odoo-tools.sh restore {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {DUMP_TO_RESTORE}"
echo -e "------------------------\n"
