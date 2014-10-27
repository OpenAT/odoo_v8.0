#!/bin/bash
#######################################################################################################################

GITPATH="https://github.com/OpenAT"
REPONAME="odoo_v8.0"
REPOID="o8"
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
MODEPREPARE="odoo-tools.sh prepare"
if [ "$SCRIPT_MODE" = "prepare" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e " $MODEPREPARE"
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
        gcc mc bzr lptools make nodejs nodejs-dev nodejs-legacy pkg-config npm -y >> $SETUP_LOG
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
    echo -e "\n\nInstall Aeroolib"
    if pip freeze | grep aeroolib ; then
        echo -e "\n\nWARNING: Aeroolib seems to be already installed!" | tee -a $SETUP_LOG
        echo -e "Please upgrade manually if needed!"
        echo -e "Aeroolib has to be at least aeroolib==1.2.0 to work with ${REPONAME}\n\n"
    else
        if [ -d ${REPO_SETUPPATH}/aeroolib ]; then
            echo -e "Do not clone aeroolib from github since directory ${REPO_SETUPPATH}/aeroolib exists ."
        else
            echo -e "Clone aeroolib from github."
            git clone --depth 1 --single-branch https://github.com/aeroo/aeroolib.git ${REPO_SETUPPATH}/aeroolib >> $SETUP_LOG
        fi
        cd ${REPO_SETUPPATH}/aeroolib >> $SETUP_LOG
        python ${REPO_SETUPPATH}/aeroolib/setup.py install | tee -a $SETUP_LOG
        if pip freeze | grep aeroolib ;  then
            echo -e "\nAeroolib is successfully installed!\n"
        else
            echo -e "\nWARNING: Could not install aeroolib\n"
        fi
        cd ${REPO_SETUPPATH} >> $SETUP_LOG
        echo -e "\nInstall Aeroo LibreOffice Service to init.d as service aeroo"
        wget -O - ${GITRAW}/TOOLS/aeroo.init > ${REPO_SETUPPATH}/aeroo.init
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
    echo -e "\n----- Install less compiler"
    hash -r
    #curl -L https://npmjs.org/install.sh | sh >> $SETUP_LOG # will not work with etherpad-lite
    npm install less >> $SETUP_LOG
    echo -e "----- Install nodejs and less compiler DONE"

    # ---- Todo: Harden linux server
    #      - enable ufw firewall (open http(s), smtp(s) ports)
    #      - set postgres to listen only on localhost

    echo -e "\n-----------------------------------------------------------------------"
    echo -e " $MODEPREPARE DONE"
    echo -e "-----------------------------------------------------------------------"
    echo -e "\n!!!PLEASE REBOOT THIS SERVER NOW!!!\n"
    exit 0
fi


# -----------------------------------------------------------------------
# $ odoo-tools.sh setup {TARGET_BRANCH}
# -----------------------------------------------------------------------
MODESETUP="odoo-tools.sh setup       {TARGET_BRANCH}"
if [ "$SCRIPT_MODE" = "setup" ]; then
    echo -e "\n-----------------------------------------------------------------------"
    echo -e "$MODESETUP"
    echo -e "-----------------------------------------------------------------------"
    echo -e "ATTENTION: You have to run \"odoo-tools.sh prepare\" before setting up your first instance!\n"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly two arguments!"
        exit 2
    fi

    # ----- Set Variables
    TARGET_BRANCH=$2
    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"

    # ----- Check if the TARGET_BRANCH already exists
    if git ls-remote ${SOURCE_REPO} | grep -sw "${TARGET_BRANCH}" 2>&1>/dev/null; then
        echo "ERROR: ${TARGET_BRANCH} already exists in ${REPONAME}!"; exit 2
    fi    

    # ----- Create Instance Log File for SETUP
    INSTANCE_SETUPLOG="${REPO_SETUPPATH}/${SCRIPT_MODE}--${TARGET_BRANCH}--`date +%Y-%m-%d__%H-%M`.log"
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

    # ----- Allow the user to check all arguments:
    echo -e ""
    echo -e "\$1 Script Mode                    :  $SCRIPT_MODE" | tee -a $INSTANCE_SETUPLOG
    echo -e "\$2 Target Branch                  :  $TARGET_BRANCH" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Instance Setuplog File            :  $INSTANCE_SETUPLOG" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Instance Branch Name              :  $TARGET_BRANCH" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance Base Directory           :  $INSTANCE_PATH" | tee -a $INSTANCE_SETUPLOG
    echo -e "Instance LINUX User               :  $TARGET_BRANCH" | tee -a $INSTANCE_SETUPLOG
    echo -e ""
    echo -e "Would you like to setup a new odoo instance with this settings? ( Y/N ): "; read answer
    if [ "${answer}" != "Y" ]; then
        while [ "${answer}" != "Y" ]; do
            if [ "${answer}" == "n" ] || [ "${answer}" == "N" ]; then
                echo "SETUP APPORTED: EXITING SCRIPT!"
                rm ${INSTANCE_SETUPLOG}
                rm -r ${INSTANCE_PATH}
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

    # ----- ToDo: install our instance in virtualenv environment
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
    echo -e "\n----- Create Instance Linux User and Group: ${TARGET_BRANCH}"
    useradd -m -s /bin/bash ${TARGET_BRANCH} | tee -a $INSTANCE_SETUPLOG

    # ----- Set Linux Rights
    chown -R ${TARGET_BRANCH}:${TARGET_BRANCH} ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG
    chmod 755 ${INSTANCE_PATH} >> $INSTANCE_SETUPLOG

    echo -e "-------------------------------------------------------------------------"
    echo -e " $MODESETUP DONE"
    echo -e "-------------------------------------------------------------------------"
    echo -e "\n!!!PLEASE UPLOAD YOUR INSTANCE TO GITHUB NOW!!!\ngit push origin $TARGET_BRANCH"
    exit 0
fi


# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh newdb {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME} {DATABASE_NAME}
# ---------------------------------------------------------------------------------------
MODENEWDB="odoo-tools.sh newdb       {TARGET_BRANCH =Instance} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME}"
MODEDUPDB="odoo-tools.sh duplicatedb {TARGET_BRANCH =Instance} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME} {DATABASE_TEMPLATE}"
if [ "$SCRIPT_MODE" = "newdb" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODENEWDB"
    echo -e "--------------------------------------------------------------------------------------------------------"
    echo -e "DATABASE_NAME should be something like: hof, hof01, db01, erp, test or demo!"
    echo -e "So customer_id (e.g.: hof) or keyword depending on the instance! Do not use \"_\" in db names!"
    if [ $# -ne 5 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly four arguments!"
        exit 2
    fi

    # INFO:
    #
    # Variable Names:
    # If it is a path usw no trailing "/" and use PATH in the variable_name:
    # So variables without PATH can be anything including files e.g. DB_SETUPLOG
    #
    # Conventions:
    # Use $REPOID (o8) for odoo_v8.0 in DBNAME to identify corresponding Repo in case other repos (_v7.0) are installed
    # on this server too. o8_ is used because postgres user- and db-names should only contain a-z 0-9 and _
    #
    # One repo can only be installed once on a server (but with many instances)
    #
    # max 99 Databases are allowed for all databases of all instances of one repo on this server because of port limit
    # see BASEPORT later down
    #
    # New Port Schema:
    # [v][dd][pp]    [v]=Odoo_Version [dd]=Database    [pp]=Instance_Services
    #  e.g.: 10169 = [1]=odoo_v8.0    [01]=database_01 [69]=port_69
    # [0]=Odoo Versions:
    #       4 = odoo OLD setups 6or7 old install
    #       1 = odoo v8.0
    #       2 = odoo v9.0
    #
    # Highest Linux Port Number (2^16)-1, or 0-65,535 (the -1 is because port 0 is reserved and unavailable)

    # ----- Set Variables
    TARGET_BRANCH=$2
    SUPER_PASSWORD=$3
    DOMAIN_NAME=$4

    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"

    DBNAME="${REPOID}_${TARGET_BRANCH}_$5"
    DBUSER="${DBNAME}"
    DBPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`

    DBPATH="${INSTANCE_PATH}/${DBNAME}"
    DBLOGPATH="/var/log/${DBNAME}"
    DBLOGFILE="${DBLOGPATH}/${DBNAME}.log"
    DB_SETUPLOG="${DBPATH}/${SCRIPT_MODE}--${DBNAME}--`date +%Y-%m-%d__%H-%M`.log"

    ETHERPADKEY=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 16 | head -1`

    # ----- TODO: Allow only lowercase a-z and 0-9 and _ in TARGET_BRANCH and DATABASE_NAME ($5) or exit 2
    # Target_Branch should be already checked at odoo-tools.sh setup
    # Maybe we only check DBNAME because everything is in there

    # ----- TODO: Check if the database name already exists (and exit with error if yes)

    # ----- Check if the TARGET_BRANCH (Instance) directory exists
    if ! [ -d ${INSTANCE_PATH} ]; then
        echo -e "ERROR: Instance Directory ${INSTANCE_PATH} is missing!"; exit 2
    fi

    # ----- Create base directory for the new database
    if [ -d "${DBPATH}" ]; then
        echo -e "ERROR: ${DBPATH} already exists!"; exit 2
    else
        if  mkdir ${DBPATH} 2>&1>/dev/null; then
            echo -e "Database Directory ${DBPATH} created."
        else
            echo -e "ERROR: Could not create directory ${DBPATH}!"; exit 2
        fi
    fi

    # ----- Create odoo addons directory for the new database
    DBADDONSPATH="${DBPATH}/addons"
    if  mkdir ${DBADDONSPATH} 2>&1>/dev/null; then
        echo -e "Database odoo addons Directory ${DBADDONSPATH} created."
    else
        echo -e "ERROR: Could not create directory ${DBADDONSPATH}!"; exit 2
    fi

    # ----- Create log directory
    if  mkdir ${DBLOGPATH} 2>&1>/dev/null; then
        echo -e "Database Log Directory ${DBLOGPATH} created."
    else
        echo -e "ERROR: Could not create directory ${DBLOGPATH}!"; exit 2
    fi

    # ----- Create setup (newdb) log file (Log from here on)
    if [ -w "${DB_SETUPLOG}" ] ; then
        echo -e "ERROR: ${DB_SETUPLOG} already exists!"; exit 2
    else
        if  touch ${DB_SETUPLOG} 2>&1>/dev/null; then
            echo -e "DB setup log file ${DB_SETUPLOG} created.\nUse tail -f ${DB_SETUPLOG} during install."
        else
            echo -e "ERROR: Could not create log file ${DB_SETUPLOG}!"; exit 2
        fi
    fi

    # ----- Set Linux Rights
    chown -R ${TARGET_BRANCH}:${TARGET_BRANCH} ${DBPATH} >> $DB_SETUPLOG
    chmod 755 ${DBPATH} >> $DB_SETUPLOG
    chown -R ${TARGET_BRANCH}:${TARGET_BRANCH} ${DBLOGPATH} >> $DB_SETUPLOG
    chmod 777 ${DBLOGPATH} >> $DB_SETUPLOG

    # ---- Read (or set) and increment BASEPORT
    COUNTERFILE=${REPO_SETUPPATH}/${REPONAME}.counter
    if [ -f ${COUNTERFILE} ]; then
        echo -e "File ${COUNTERFILE} exists."
    else
        if  touch ${COUNTERFILE} 2>&1>/dev/null; then
            # SEE INFO ABOVE!
            echo -e "100" > ${COUNTERFILE};
            echo -e "File ${COUNTERFILE} created."
        else
            echo -e "ERROR: Could not create file ${COUNTERFILE}!"
            exit 2
        fi
    fi
    typeset -i BASEPORT
    BASEPORT=`cat ${COUNTERFILE}`+1
    if [ ${BASEPORT} -lt 100 ]; then
        echo echo -e "ERROR: Could not update or read BASEPORT (${BASEPORT}) !"; exit 2
    fi
    echo ${BASEPORT} > ${COUNTERFILE}

    # ----- Allow the user to check all arguments:
    echo -e ""
    echo -e "\$1 Script Mode                    :  $SCRIPT_MODE" | tee -a $DB_SETUPLOG
    echo -e "\$2 TARGET_BRANCH                  :  $TARGET_BRANCH" | tee -a $DB_SETUPLOG
    echo -e "\$3 SUPER_PASSWORD                 :  $SUPER_PASSWORD" | tee -a $DB_SETUPLOG
    echo -e "\$4 DOMAIN_NAME                    :  $DOMAIN_NAME" | tee -a $DB_SETUPLOG
    echo -e "\$5 DATABASE_NAME                  :  $5" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "Database Setup Log File           :  $DB_SETUPLOG" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "Database FINAL Name               :  $DBNAME" | tee -a $DB_SETUPLOG
    echo -e "Database Directory                :  $DBPATH" | tee -a $DB_SETUPLOG
    echo -e "Database Logfile                  :  $DBLOGFILE" | tee -a $DB_SETUPLOG
    echo -e "Database Baseport                 :  $BASEPORT" | tee -a $DB_SETUPLOG
    echo -e "Database Database User Name       :  $DBUSER" | tee -a $DB_SETUPLOG
    echo -e "Database Database User Password   :  $DBPW" | tee -a $DB_SETUPLOG
    echo -e "Database LINUX User               :  $TARGET_BRANCH" | tee -a $DB_SETUPLOG
    echo -e "Database Etherpad SESSION KEY     :  $ETHERPADKEY" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "ATTENTION: The password for the admin user of the new database will be \"adminpw\"!\n"
    echo -e "Would you like to setup a new odoo database ${DBNAME} at ${DBPATH} with this settings?"
    echo -e "Please enter Y (Yes) or N (No):"; read answer
    if [ "${answer}" != "Y" ]; then
        while [ "${answer}" != "Y" ]; do
            if [ "${answer}" == "n" ] || [ "${answer}" == "N" ]; then
                echo "SETUP APPORTED: EXITING SCRIPT!"
                echo -e "Removing directory ${DBLOGPATH}"
                rm -r ${DBLOGPATH}
                echo -e "Removing directory ${DBPATH}"
                rm -r ${DBPATH}
                BASEPORT=${BASEPORT}-1
                echo -e "Resetting BASEPORT to: ${BASEPORT}"
                echo ${BASEPORT} > ${COUNTERFILE}
                exit 1
            fi
            echo "Please enter Y (Yes) or N (No): "; read answer
        done
    fi


    # ----- Create Database User
    echo -e "\n---- Create postgresql role $DBUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${DBUSER}' WITH NOSUPERUSER CREATEDB LOGIN PASSWORD '\'${DBPW}\''"' | tee -a $DB_SETUPLOG

    # ----- Create server.conf
    DBCONF=${DBPATH}/${DBNAME}.conf
    echo -e "\n---- Create DB odoo server config file: ${DBCONF}"
    /bin/sed '{
        s!'"addons_path = odoo/openerp/addons,odoo/addons,addons-loaded"'!'"addons_path = ${INSTANCE_PATH}/odoo/openerp/addons,${INSTANCE_PATH}/odoo/addons,${INSTANCE_PATH}/addons-loaded,${DBADDONSPATH}"'!g
        s!'"admin_passwd = admin"'!'"admin_passwd = ${SUPER_PASSWORD}"'!g
        s!'"data_dir = data_dir"'!'"data_dir = ${DBPATH}/data_dir"'!g
        s!'"db_password = odoo"'!'"db_password = ${DBPW}"'!g
        s!'"db_user = odoo"'!'"db_user = ${DBUSER}"'!g
        s!'"logfile = None"'!'"logfile = ${DBLOGFILE}"'!g
        s!'"logrotate = False"'!'"logrotate = True"'!g
        s!'"longpolling_port = 8072"'!'"longpolling_port = ${BASEPORT}72"'!g
        s!'"xmlrpc_port = 8069"'!'"xmlrpc_port = ${BASEPORT}69"'!g
        s!'"xmlrpcs_port = 8071"'!'"xmlrpcs_port = ${BASEPORT}71"'!g
        }' ${INSTANCE_PATH}/TOOLS/server.conf > ${DBCONF} | tee -a $DB_SETUPLOG
    chown root:root ${DBCONF}
    chmod ugo=r ${DBCONF}


    # ----- Create the Init Script for odoo
    echo -e "\n---- Setup init.d for instance: ${INSTANCE_PATH}/${TARGET_BRANCH}.init"
    DBINIT=${DBPATH}/${DBNAME}.init
    /bin/sed '{
        s!'"DAEMON=INSTANCE_PATH/odoo/openerp-server"'!'"DAEMON=${INSTANCE_PATH}/odoo/openerp-server"'!g
        s!'"USER="'!'"USER=${TARGET_BRANCH}"'!g
        s!'"CONFIGFILE="'!'"CONFIGFILE=${DBCONF}"'!g
        s!'"DAEMON_OPTS="'!'"DAEMON_OPTS=\"-c ${DBCONF} -d ${DBNAME} --db-filter=^${DBNAME}$\""'!g
        s!DBNAME!'"$DBNAME"'!g
        }' ${INSTANCE_PATH}/TOOLS/server.init > ${DBINIT} | tee -a $DB_SETUPLOG
    chown root:root ${DBINIT}
    chmod ugo=rx ${DBINIT}
    ln -s ${DBINIT} /etc/init.d/${DBNAME} | tee -a $DB_SETUPLOG
    update-rc.d ${DBNAME} defaults | tee -a $DB_SETUPLOG
    service ${DBNAME} start | tee -a $DB_SETUPLOG
    echo -e "Wait 8s for service ${DBNAME} to start..."
    sleep 8

    # ----- Create a new Database
    echo -e "\n----- Create Database ${DBNAME}"
    chmod 775 ${INSTANCE_PATH}/TOOLS/create_db.py
    if ${INSTANCE_PATH}/TOOLS/db-tools.py -b ${BASEPORT}69 -s $SUPER_PASSWORD newdb -d $DBNAME -p adminpw ; then
        echo -e "Database created!" | tee -a $DB_SETUPLOG
    else
        echo -e "WARNING: Could not create Database ${DBNAME} !\nPlease create it manually!" | tee -a $DB_SETUPLOG
    fi

    # ----- Link Log Folder
    echo -e "\n---- Link ${DBLOGPATH} to ${DBPATH}/LOG"
    ln -s ${DBLOGPATH} ${DBPATH}/LOG | tee -a $DB_SETUPLOG

    # ----- Setup nginx
    echo -e "---- Create NGINX config file"
    NGINXCONF=${DBPATH}/${DBNAME}-nginx.conf
    /bin/sed '{
        s!BASEPORT!'"${BASEPORT}"'!g
        s!DBNAME!'"${DBNAME}"'!g
        s!DOMAIN_NAME!'"${DOMAIN_NAME}"'!g
        s!DBLOGPATH!'"${DBLOGPATH}"'!g
            }' ${INSTANCE_PATH}/TOOLS/nginx.conf > ${NGINXCONF} | tee -a $DB_SETUPLOG
    chown root:root ${NGINXCONF}
    chmod ugo=r ${NGINXCONF}
    ln -s ${NGINXCONF}  /etc/nginx/sites-enabled/${DBNAME}-${DOMAIN_NAME}
    service nginx restart
    echo -e "---- Create NGINX config file DONE"

    # ----- Setup Etherpad-Lite
    echo -e "---- Setup Etherpad-Lite"
    PADLOG=${DBLOGPATH}/${DBNAME}-pad.log
    PADCONF=${DBPATH}/${DBNAME}-pad.conf
    PADINIT=${DBPATH}/${DBNAME}-pad.init
    # Create the etherpad database (utf8)
    echo -e "Create DB for etherpad lite: ${DBNAME}_pad Owner: ${DBUSER}"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE DATABASE '${DBNAME}'_pad WITH OWNER '${DBUSER}' ENCODING '\'UTF8\''" ' | tee -a $DB_SETUPLOG
    # etherpad-lite config file
    echo -e "Create etherpad config file"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!TARGET_BRANCH!'"$TARGET_BRANCH"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!DBUSER!'"$DBUSER"'!g
        s!DBPW!'"$DBPW"'!g
        s!DBNAME!'"$DBNAME"'!g
        s!ETHERPADKEY!'"$ETHERPADKEY"'!g
        s!PADLOG!'"$PADLOG"'!g
        }' ${INSTANCE_PATH}/TOOLS/etherpad.conf > ${PADCONF} | tee -a $DB_SETUPLOG
    chown root:root ${PADCONF}
    chmod ugo=r ${PADCONF}
    # etherpad-lite init file
    echo -e "Create etherpad init file and start service"
    /bin/sed '{
        s!DBUSER!'"$DBUSER"'!g
        s!INSTANCE_PATH!'"$INSTANCE_PATH"'!g
        s!TARGET_BRANCH!'"$TARGET_BRANCH"'!g
        s!DBNAME!'"$DBNAME"'!g
        s!PADCONF!'"$PADCONF"'!g
        }' ${INSTANCE_PATH}/TOOLS/etherpad.init > ${PADINIT} | tee -a $DB_SETUPLOG
    chown root:root ${PADINIT}
    chmod ugo=rx ${PADINIT}
    ln -s ${PADINIT} /etc/init.d/${DBNAME}-pad | tee -a $DB_SETUPLOG
    update-rc.d ${DBNAME}-pad defaults | tee -a $DB_SETUPLOG
    service ${DBNAME}-pad start

    # TODO ----- Setup cron Logrotate for all Logfiles

    # TODO ----- Setup cron job for backup script(s)

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODENEWDB DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    echo -e "\nAfter database install you should follow these steps:"
    echo -e ""
    echo -e "1) Open http://$DOMAIN_NAME (admin password is \"adminpw\")."
    echo -e "2) Install the addon base_config in your new DB $DBNAME."
    echo -e "3) During install of base_config select austrian-chart-of-account and 20%-Mwst and 20%-Vst."
    echo -e "4) After install set time period to month for HR."
    echo -e "5) Enable Colaborative Pads at URL http://$DOMAIN_NAME/pad (PWD: $SUPER_PASSWORD)"
    echo -e "   You will find the API-KEY at: $INSTANCE_PATH/etherpad-lite/APIKEY.txt"
    echo -e "   ATTENTION: First start of etherpad-lite takes a long time. Be patient - APIKEY will show up after first start!"
    echo -e "\n Optional:"
    echo -e "1) Set Company Details"
    echo -e "2) Set Timezone, Signature and Mail-Options for Admin and Default user"
    echo -e "3) Set RealTime Warehouse Accounts for Product Categories: Maybe obsolete in v8 new wms?"
    exit 0
fi



# ---------------------------------------------------------
# Script HELP
# ---------------------------------------------------------
echo -e "\n----- SCRIPT USAGE -----"
echo -e "$ odoo-tools.sh {prepare|setup|newdb|dupdb|deploy|backup|restore}\n"
echo -e "$ $MODEPREPARE"
echo -e "$ $MODESETUP"
echo -e "$ $MODENEWDB"
echo -e "TODO: $ odoo-tools.sh dupdb"
echo -e "TODO: $ odoo-tools.sh updateinst  {TARGET_BRANCH}"
echo -e "TODO: $ odoo-tools.sh deployaddon {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "TODO: $ odoo-tools.sh backup      {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all}"
echo -e "TODO: $ odoo-tools.sh restore     {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {BACKUPFILE_TO_RESTORE}"
echo -e "------------------------\n"
