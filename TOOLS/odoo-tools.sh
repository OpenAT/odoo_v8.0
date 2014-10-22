#!/bin/bash
#######################################################################################################################

SOURCE_REPO="odoo_v8.0"
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

# ----- Base Path for all odoo instances:
BASEPATH="/opt/odoo"
if [ -d ${BASEPATH} ]; then
    echo -e "Directory ${BASEPATH} exists."
else
    if mkdir ${BASEPATH} ; then
	    echo -e "Created directory ${BASEPATH}"
    else
        echo -e "ERROR: Could not create directory $BASEPATH!"; exit 2
    fi
fi

# ----- Repo Path for all odoo instances:
REPOPATH="/opt/odoo/${SOURCE_REPO}"
if [ -d ${REPOPATH} ]; then
    echo -e "Directory ${REPOPATH} exists."
else
    if  mkdir ${REPOPATH} ; then
	    echo -e "Created directory ${REPOPATH}"
    else
        echo -e "ERROR: Could not create directory REPOPATH!"; exit 2
    fi
fi

# ----- Base Log Files Path for all odoo instances:
LOGPATH="/var/log/${SOURCE_REPO}"
if [ -d ${LOGPATH} ]; then
    echo -e "Directory ${LOGPATH} exists."
else
    if  mkdir ${LOGPATH} ; then
	    echo -e "Created directory ${LOGPATH}"
    else
        echo -e "ERROR: Could not create directory ${LOGPATH}!"; exit 2
    fi
fi

# ----- SETUP LOG-File:
SETUP_LOG="${BASEPATH}/odoo_setup.log"
if [ -w "$SETUP_LOG" ] ; then
    echo -e "Setup log file: ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
else
    if  touch $SETUP_LOG ; then
        echo -e "Setup log file ist at ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
    else
        echo -e "ERROR: Could not create log file ${SETUP_LOG}!"
	    exit 2
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


# ---------------------------------------------------------
# $ odoo-tools.sh PREPARE
# ---------------------------------------------------------
if [ "$SCRIPT_MODE" = "prepare" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh prepare"
    echo -e "-----------------------------------------------------------------------"
    if [ $# -ne 1 ]; then
        echo -e "ERROR: \"setup-toosl.sh prepare\" takes exactly one argument!"
        exit 2
    fi
    cd ${BASEPATH}

    # ----- Update Server
    echo -e "\n----- Update Server"
    apt-get update >> $SETUP_LOG
    apt-get upgrade -y >> $SETUP_LOG
    echo -e "----- Update Server Done"

    # ----- Install Basic Packages
    echo -e "\n----- Install Basic Packages"
    apt-get install ssh wget sed git git-core gzip curl python libssl-dev build-essential -y >> $SETUP_LOG
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
    echo -e "\n----- Install Python Packages"
    apt-get install python-pip python-dev python-software-properties python-pychart libxml2-dev libxslt-dev \
        python-genshi python-pyhyphen -y >> $SETUP_LOG
    apt-get install libjpeg-dev libjpeg8-dev libtiff5-dev vflib3-dev pngtools libpng3 -y >> $SETUP_LOG
    apt-get install xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic -y >> $SETUP_LOG
    apt-get install wkhtmltopdf -y >> $SETUP_LOG
    apt-get install flashplugin-nonfree -y >> $SETUP_LOG
    pip install git+https://github.com/qoda/python-wkhtmltopdf.git >> $SETUP_LOG
    echo -e "Install requirements.txt"
    wget -O - https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/TOOLS/requirements.txt > $BASEPATH/requirements.txt
    pip install -r $BASEPATH/requirements.txt >> $SETUP_LOG
    echo -e "----- Install Python Packages Done"

    # ----- Install Packages for AerooReports
    echo -e "\n----- Install Packages for AerooReports"
    apt-get install ure uno-libs3 unoconv \
                    libreoffice-core libreoffice-common libreoffice-base libreoffice-base-core \
                    libreoffice-draw libreoffice-calc libreoffice-writer libreoffice-impress \
                    python-cupshelpers hyphen-de hyphen-en-us -y >> $SETUP_LOG
    echo -e "\nInstall Aeroolib"
    git clone --depth 1 --single-branch https://github.com/aeroo/aeroolib.git $BASEPATH/aeroolib >> $SETUP_LOG
    cd $BASEPATH/aeroolib
    python $BASEPATH/aeroolib/aeroolib/setup.py install | tee -a $SETUP_LOG
    cd $BASEPATH
    echo -e "\nInstall Aeroo LibreOffice Service"
    wget -O - https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/TOOLS/aeroo.init > $BASEPATH/aeroo.init
    chmod ugo=rx $BASEPATH/aeroo.init
    ln -s $BASEPATH/aeroo.init /etc/init.d/aeroo >> $SETUP_LOG
    update-rc.d aeroo defaults >> $SETUP_LOG
    service aeroo stop
    service aeroo start
    echo -e "----- Install Packages for AerooReports Done"

    # ----- Install Packages for Etherpad Lite
    echo -e "\n----- Install Packages for Etherpad Lite"
    apt-get install nodejs abiword -y >> $SETUP_LOG
    echo -e "----- Install Packages for Etherpad Lite Done"

fi

# -----------------------------------------------------------------------
# $ odoo-tools.sh setup {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}
# -----------------------------------------------------------------------
if [ "$SCRIPT_MODE" = "setup" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " odoo-tools.sh setup {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}"
    echo -e "-----------------------------------------------------------------------"
    echo -e " You have to run \"odoo-tools.sh prepare\" before setting up your first instance!"
    if [ $# -ne 4 ]; then
        echo -e "ERROR: \"setup-toosl.sh prepare\" takes exactly four arguments!"
        exit 2
    fi

    # ----- Set CMD Variables
    TARGET_BRANCH=$2
    SUPER_PASSWORD=$3
    DOMAIN_NAME=$4

    # ----- Create Instance Directory
    INSTANCE_PATH="${BASEPATH}/${SOURCE_REPO}/${TARGET_BRANCH}"
    #if [ -d ${INSTANCE_PATH} ]; then
    #    echo -e "ERROR: ${INSTANCE_PATH} already exists!"; exit 2
    #else
    #    if mkdir ${INSTANCE_PATH} ; then
    #        echo -e "Created directory ${INSTANCE_PATH}"
    #        cd ${INSTANCE_PATH}
    #        echo -e "Changed directory to ${INSTANCE_PATH}"
    #    else
    #        echo -e "ERROR: Could not create directory ${INSTANCE_PATH}!"
    #        exit 2
    #    fi
    #fi

    # ----- Create Instance Log File for SETUP
    INSTANCE_SETUPLOG="$BASEPATH/${TARGET_BRANCH}_setup.log"
    if [ -w "${INSTANCE_SETUPLOG}" ] ; then
        echo -e "ERROR: ${INSTANCE_SETUPLOG} already exists!"
        exit 2
    else
        if  touch ${INSTANCE_SETUPLOG} ; then
            echo -e "Instance-Setup-Log: ${INSTANCE_SETUPLOG}. DO NOT MODIFY OR DELETE!"
        else
            echo -e "ERROR: Could not create log file ${INSTANCE_SETUPLOG}!"
            exit 2
        fi
    fi

    # ----- Prepare Log Directory and Variable
    INSTANCE_LOGPATH="${LOGPATH}/${SOURCE_REPO}"
    INSTANCE_LOGFILE="${INSTANCE_LOGPATH}/${TARGET_BRANCH}.log"
    if [ -d "${INSTANCE_LOGPATH}" ] ; then
        echo -e "ERROR: ${INSTANCE_LOGPATH} already exists!"
        exit 2
    else
        if  mkdir ${INSTANCE_LOGPATH} ; then
            echo -e "Instance-Log-Directory created: ${INSTANCE_LOGPATH}."
        else
            echo -e "ERROR: Could not create log directory ${INSTANCE_LOGPATH}!"
            exit 2
        fi
    fi
    chown ${DBUSER}:${DBUSER} ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG
    chmod ug=rw ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG
    chmod o=r ${INSTANCE_LOGPATH} >> $INSTANCE_SETUPLOG

    # ---- Set BASEPORT
    COUNTERFILE=$BASEPATH/INSTANCE.counter
    if [ -f ${COUNTERFILE} ]; then
        echo -e "File ${COUNTERFILE} exists."
    else
        if  touch ${COUNTERFILE} ; then
            echo -e "40" > ${COUNTERFILE};
            echo -e "File ${COUNTERFILE} created."
        else
            echo -e "ERROR: Could not create file ${COUNTERFILE}!"
            exit 2
        fi
    fi
    typeset -i BASEPORT
    BASEPORT=`cat ${COUNTERFILE}`+1
    if [ ${BASEPORT} -lt 40 ]; then
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
                rm -f ${INSTANCE_PATH}
                rm -f ${INSTANCE_LOGPATH}
                exit 1
            fi
            echo "Please enter Y (Yes) or N (No)"; read answer
        done
    fi

    # ----- Clone the Github Repo (Directory created here first!)
    echo -e "\n---- Clone the Github Repo ${SOURCE_REPO}"
    git clone -b master --depth 1 --single-branch --recurse-submodules \
        https://github.com/OpenAT/${SOURCE_REPO}.git ${INSTANCE_PATH} | tee -a $INSTANCE_SETUPLOG
    cd ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG
    git branch ${TARGET_BRANCH} >> $INSTANCE_SETUPLOG
    git checkout ${TARGET_BRANCH} >> $INSTANCE_SETUPLOG
    if [ ! -d "${INSTANCE_PATH}/odoo" ]; then
        echo -e "ERROR: Cloning the github repo failed!"; exit 2
    fi

    # ----- Setup the Linux User and Group
    echo -e "\n----- Create Instance Linux User and Group: ${DBUSER}"
    useradd -m -s /bin/bash ${DBUSER} | tee -a $INSTANCE_SETUPLOG

    # ----- Create Database User
    echo -e "\n---- Create postgresql role $DBUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${DBUSER}' WITH NOSUPERUSER CREATEDB LOGIN PASSWORD '\'${DBPW}\''"' | tee -a $INSTANCE_SETUPLOG

    # ---- Create server.conf
    echo -e "\n---- Create odoo server config in: ${INSTANCE_PATH}/${TARGET_BRANCH}.conf"
    /bin/sed '{
        s,"admin_passwd = admin",'"admin_passwd = ${SUPER_PASSWORD}"',g
        s,"data_dir = data_dir",'"data_dir = ${INSTANCE_PATH}/data_dir"',g
        s,"db_password = odoo",'"db_password = ${DBPW}"',g
        s,"db_user = odoo",'"db_user = ${DBUSER}"',g
        s,"logfile = None",'"logfile = ${INSTANCE_LOGFILE}"',g
        s,"longpolling_port = 8072",'"longpolling_port = ${BASEPORT}8072"',g
        s,"xmlrpc_port = 8069",'"xmlrpc_port = ${BASEPORT}8069"',g
        s,"xmlrpcs_port = 8071",'"xmlrpcs_port = ${BASEPORT}8071"',g
            }' ${INSTANCE_PATH}/TOOLS/server.conf > ${INSTANCE_PATH}/${TARGET_BRANCH}.conf | tee -a $INSTANCE_SETUPLOG
        chown ${DBUSER}:${DBUSER} ${INSTANCE_PATH}/${TARGET_BRANCH}.conf
        chmod ugo=r ${INSTANCE_PATH}/${TARGET_BRANCH}.conf

    # ---- Create the Init Script for odoo
    echo -e "\n---- Setup init.d for instance: ${INSTANCE_PATH}/${TARGET_BRANCH}.init"
    /bin/sed '{
        s,DBUSER,'"$DBUSER"',g
        s,TARGET_BRANCH,'"$TARGET_BRANCH"',g
        s,INSTANCE_PATH,'"$INSTANCE_PATH"',g
            }' ${INSTANCE_PATH}/TOOLS/server.init > ${INSTANCE_PATH}/${TARGET_BRANCH}.init | tee -a $INSTANCE_SETUPLOG
    chmod ugo=rx ${INSTANCE_PATH}/${TARGET_BRANCH}.init
    ln -s ${INSTANCE_PATH}/${TARGET_BRANCH}.init /etc/init.d/${TARGET_BRANCH} | tee -a $INSTANCE_SETUPLOG
    update-rc.d ${TARGET_BRANCH} defaults | tee -a $INSTANCE_SETUPLOG
    service ${TARGET_BRANCH} start | tee -a $INSTANCE_SETUPLOG

    # ----- Link Log File (should be there after first start!)
    if [ -s ${INSTANCE_LOGFILE} ]; then
        echo -e "----------\nWARNING: Log file for instance was NOT created!\n----------"
    else
        ln -s ${INSTANCE_LOGFILE} ${INSTANCE_PATH}
    fi


    # ----- Setup nginx # INFO Maybe check the proxy setting from v7 because of nginx ;)

    # ----- Setup Etherpad-Lite
    # ----- Setup cron Logrotate for all Logfiles
    # ----- Setup cron backup script

    # Maybe: Test URL to database - should work with v8.0

fi


# ---------------------------------------------------------
# Script HELP
# ---------------------------------------------------------
echo -e "\n----- SCRIPT USAGE -----"
echo -e "$ odoo-tools.sh {prepare|setup|deploy|backup|restore} ...\n"
echo -e "$ odoo-tools.sh prepare"
echo -e "$ odoo-tools.sh setup   {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}"
echo -e "$ odoo-tools.sh deploy  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "$ odoo-tools.sh backup  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all}"
echo -e "$ odoo-tools.sh restore {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {DUMP_TO_RESTORE}"
echo -e "------------------------\n"
