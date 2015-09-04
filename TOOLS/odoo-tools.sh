#!/bin/bash
#######################################################################################################################

GITPATH="https://github.com/OpenAT"
REPONAME="odoo_v8.0"
REPOID="o8"
SOURCE_REPO=${GITPATH}/${REPONAME}.git
FPMCONFIGPATH=/etc/php5/fpm/pool.d/www.conf
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
    update-rc.d -f postgresql remove
    update-rc.d postgresql start 19 2 3 5 . stop 81 0 1 4 6 . >> $SETUP_LOG
    service postgresql restart | tee -a $SETUP_LOG
    echo -e "----- Install postgresql Done"

    # ----- Install nginx
    echo -e "\n----- Install nginx"
    apt-get remove apache2 apache2-mpm-event apache2-mpm-prefork apache2-mpm-worker -y >> $SETUP_LOG
    apt-get install nginx -y >> $SETUP_LOG
    update-rc.d -f nginx remove
    update-rc.d nginx start 20 2 3 5 . stop 80 0 1 4 6 . >> $SETUP_LOG
    service nginx restart | tee -a $SETUP_LOG
    touch /usr/share/nginx/html/maintenance_aus.html >>$SETUP_LOG
    echo -e "----- Install nginx Done"

    # ----- Install Python Packages
    echo -e "\n----- Install Python Apt Packages"
    apt-get install libldap2-dev libsasl2-dev python-pip python-virtualenv python-dev python-software-properties python-pychart \
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
        wget http://sourceforge.net/projects/wkhtmltopdf/files/archive/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb >> $SETUP_LOG
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

    # ----- Make sure Pil is used not Pillow
    echo -e "\n----- Make sure Pil is used and not Pillow"
    apt-get remove pil pillow -y >> $SETUP_LOG
    pip uninstall pil
    pip uninstall pillow
    apt-get install libjpeg-dev libfreetype6-dev zlib1g-dev libtiff4 libtiff4-dev python-libtiff -y >> $SETUP_LOG
    pip install Pillow==2.5.1 --upgrade

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
        update-rc.d -f aeroo remove
        update-rc.d aeroo start 20 2 3 5 . stop 80 0 1 4 6 . >> $SETUP_LOG
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

    # ----- Install packages for owncloud
    echo -e "\n----- Install packages for owncloud"
    apt-get install php5-fpm -y >> $SETUP_LOG
    apt-get install php5-cgi php5-pgsql php5-gd php5-curl php5-intl php5-mcrypt php5-ldap php5-gmp php5-imagick \
                    libav-tools php5-readline -y >> $SETUP_LOG
    # --- Make sure PHP-FPM is listening on unix socket and not on IP!
    if /bin/grep -q "listen = 127.0.0.1:9000" ${FPMCONFIGPATH} ; then
        sed -i "s|listen = 127.0.0.1:9000|listen = /var/run/php5-fpm.sock|g" ${FPMCONFIGPATH}
    fi
    update-rc.d -f apache2 disable >> $SETUP_LOG
    echo -e "\n----- Install packages for done"


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
        echo "WARNING: ${TARGET_BRANCH} already exists in ${REPONAME}!";
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

    # ----- create webserver maintenance files
    cp ${INSTANCE_PATH}/TOOLS/503.* /usr/share/nginx/html/ >> $INSTANCE_SETUPLOG


    echo -e "-------------------------------------------------------------------------"
    echo -e " $MODESETUP DONE"
    echo -e "-------------------------------------------------------------------------"
    echo -e "\n!!!START EHTERPAD-LITE now with run.sh to create the APIKEY.txt!!!"
    echo -e "\n!!!PLEASE UPLOAD YOUR INSTANCE TO GITHUB NOW!!!\ngit push origin $TARGET_BRANCH"
    exit 0
fi


# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh newdb {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME} {DATABASE_NAME}
# ---------------------------------------------------------------------------------------
MODENEWDB="odoo-tools.sh newdb       {TARGET_BRANCH} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME}"
MODEDUPDB="odoo-tools.sh duplicatedb {TARGET_BRANCH} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME} {DATABASE_TEMPLATE}"
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
    DOMAIN_NAME=$5

    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"

    DBNAME="${REPOID}_${TARGET_BRANCH}_$4"
    DBUSER="${DBNAME}"
    DBPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`

    LINUXPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`

    DBPATH="${INSTANCE_PATH}/${DBNAME}"
    DBLOGPATH="/var/log/${DBNAME}"
    DBLOGFILE="${DBLOGPATH}/${DBNAME}.log"
    DBBACKUPPATH="${DBPATH}/BACKUP"
    DB_SETUPLOG="${DBPATH}/${SCRIPT_MODE}--${DBNAME}--`date +%Y-%m-%d__%H-%M`.log"

    ETHERPADKEY=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 16 | head -1`

    # ----- Basic Checks

    # todo Allow only lowercase a-z and 0-9 and _ in DBNAME (= TARGET_BRANCH and DATABASE_NAME)

    # Check if a database with this name already exists (and exit with error if yes)
    if [ `su - postgres -c "psql -l | grep ${DBNAME} | wc -l"` -gt 0 ]; then
        echo -e "ERROR: Database ${DBNAME} already exists!"
        exit 2
    fi

    # Check if the domain already exists in any nginx conf file
    if grep -i -r "${DOMAIN_NAME}" /etc/nginx/sites-enabled/* ; then
        echo -e "ERROR: Domain Name ${DOMAIN_NAME} already used in a nginx config file in /etc/nginx/sites-enabled/"
        exit 2
    fi

    # Check if the TARGET_BRANCH (Instance) directory exists
    if ! [ -d ${INSTANCE_PATH} ]; then
        echo -e "ERROR: Instance Directory ${INSTANCE_PATH} is missing!"; exit 2
    fi


    # ----- Setup the Linux User and Group and create it's Home Directory
    echo -e "\n----- Create Instance Linux User and Group: ${DBUSER}"
    useradd -m -d ${DBPATH} -s /bin/bash -U -G ${TARGET_BRANCH} -p $(echo "${LINUXPW}" | openssl passwd -1 -stdin) ${DBUSER} | tee -a $INSTANCE_SETUPLOG

    # create sudoers file
    echo "${DBUSER} ALL=(root) NOPASSWD: /usr/bin/service ${DBNAME} restart, /usr/bin/service ${DBNAME} stop, /usr/bin/service ${DBNAME} start" > ${DBPATH}/${DBUSER}.sudo
    echo "${DBUSER} ALL=(root) NOPASSWD: /usr/bin/service ${DBNAME}-pad restart, /usr/bin/service ${DBNAME}-pad stop, /usr/bin/service ${DBNAME}-pad start" >> ${DBPATH}/${DBUSER}.sudo
    ln -s ${DBPATH}/${DBUSER}.sudo /etc/sudoers.d/${DBUSER}.sudo

    # Check if the home dir was created
    if [ -d "${DBPATH}" ]; then
        echo -e "Database Directory ${DBPATH} exists."
    else
        echo -e "ERROR: ${DBPATH} could not be created!"; exit 2
    fi

    # ----- Create BACKUP directory
    if  mkdir ${DBBACKUPPATH} 2>&1>/dev/null; then
        echo -e "Database BACKUP Directory ${DBBACKUPPATH} created."
    else
        echo -e "ERROR: Could not create directory ${DBBACKUPPATH}!"; exit 2
    fi

    # ----- Create odoo ADDONS directory
    DBADDONSPATH="${DBPATH}/addons"
    if  mkdir ${DBADDONSPATH} 2>&1>/dev/null; then
        echo -e "Database odoo addons Directory ${DBADDONSPATH} created."
    else
        echo -e "ERROR: Could not create directory ${DBADDONSPATH}!"; exit 2
    fi

    # ----- Create LOG directory
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
    chown -R ${DBUSER}:${DBUSER} ${DBPATH} >> $DB_SETUPLOG
    chmod 755 ${DBPATH} >> $DB_SETUPLOG
    chown -R ${DBUSER}:${DBUSER} ${DBLOGPATH} >> $DB_SETUPLOG
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
    echo -e "\$4 DATABASE_NAME                  :  $4" | tee -a $DB_SETUPLOG
    echo -e "\$5 DOMAIN_NAME                    :  $DOMAIN_NAME" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "Database Setup Log File           :  $DB_SETUPLOG" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "Database FINAL Name               :  $DBNAME" | tee -a $DB_SETUPLOG
    echo -e "Database Directory                :  $DBPATH" | tee -a $DB_SETUPLOG
    echo -e "Database Logfile                  :  $DBLOGFILE" | tee -a $DB_SETUPLOG
    echo -e "Database Baseport                 :  $BASEPORT" | tee -a $DB_SETUPLOG
    echo -e "Database Database User Name       :  $DBUSER" | tee -a $DB_SETUPLOG
    echo -e "Database Database User Password   :  $DBPW" | tee -a $DB_SETUPLOG
    echo -e "Database LINUX User               :  $DBUSER" | tee -a $DB_SETUPLOG
    echo -e "Database LINUX User Password      :  $LINUXPW" | tee -a $DB_SETUPLOG
    echo -e "Database Etherpad SESSION KEY     :  $ETHERPADKEY" | tee -a $DB_SETUPLOG
    echo -e ""
    echo -e "ATTENTION: The password for the admin user of the new database will be \"adminpw\"!\n"
    echo -e "Would you like to setup a new odoo database ${DBNAME} at ${DBPATH} with this settings?"
    echo -e "Please enter Y (Yes) or N (No):"; read answer
    if [ "${answer}" != "Y" ]; then
        while [ "${answer}" != "Y" ]; do
            if [ "${answer}" == "n" ] || [ "${answer}" == "N" ]; then
                echo "SETUP APPORTED: EXITING SCRIPT!"
                echo -e "Removing log directory ${DBLOGPATH}"
                rm -r ${DBLOGPATH}
                echo -e "Removing Linux user ${DBNAME} and home directory ${DBPATH}"
                userdel -r ${DBNAME}
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
    DBINIT=${DBPATH}/${DBNAME}.init
    echo -e "\n---- Setup init.d for instance: ${DBINIT}"
    /bin/sed '{
        s!'"DAEMON=INSTANCE_PATH/odoo/openerp-server"'!'"DAEMON=${INSTANCE_PATH}/odoo/openerp-server"'!g
        s!'"USER="'!'"USER=${DBUSER}"'!g
        s!'"CONFIGFILE="'!'"CONFIGFILE=${DBCONF}"'!g
        s!'"DAEMON_OPTS="'!'"DAEMON_OPTS=\"-c ${DBCONF} -d ${DBNAME} --db-filter=^${DBNAME}$\""'!g
        s!DBNAME!'"$DBNAME"'!g
        }' ${INSTANCE_PATH}/TOOLS/server.init > ${DBINIT} | tee -a $DB_SETUPLOG
    chown root:root ${DBINIT}
    chmod ugo=rx ${DBINIT}
    ln -s ${DBINIT} /etc/init.d/${DBNAME} | tee -a $DB_SETUPLOG
    update-rc.d ${DBNAME} start 20 2 3 5 . stop 80 0 1 4 6 . | tee -a $DB_SETUPLOG
    service ${DBNAME} start | tee -a $DB_SETUPLOG
    echo -e "Wait 8s for service ${DBNAME} to start..."
    sleep 8

    # ----- Create a new Database
    echo -e "\n----- Create Database ${DBNAME}"
    chmod 775 ${INSTANCE_PATH}/TOOLS/db-tools.py
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
    NGINXDBMAINTENANCEONLYFILE=${DBPATH}/${DBNAME}-maintenance
    /bin/sed '{
        s!BASEPORT!'"${BASEPORT}"'!g
        s!DBNAME!'"${DBNAME}"'!g
        s!DOMAIN_NAME!'"${DOMAIN_NAME}"'!g
        s!DBLOGPATH!'"${DBLOGPATH}"'!g
        s!DBPATH!'"${DBPATH}"'!g
        s!MAINTENANCEMODE!'"${NGINXDBMAINTENANCEONLYFILE}_ein"'!g
            }' ${INSTANCE_PATH}/TOOLS/nginx.conf > ${NGINXCONF} | tee -a $DB_SETUPLOG
    chown root:root ${NGINXCONF}
    chmod ugo=r ${NGINXCONF}
    touch ${DBMAINTENANCEONLYFILE}_aus
    ln -s ${NGINXCONF}  /etc/nginx/sites-enabled/${DBNAME}-${DOMAIN_NAME}
    service nginx restart
    echo -e "---- Create NGINX config file DONE"

    # ----- Setup Etherpad-Lite
    echo -e "\n---- Setup Etherpad-Lite"
    PADLOG=${DBLOGPATH}/${DBNAME}-pad.log
    PADCONF=${DBPATH}/${DBNAME}-pad.conf
    PADINIT=${DBPATH}/${DBNAME}-pad.init
    PADPATH=${DBPATH}/etherpad-lite
    PADDB=${DBNAME}_pad
    PADUSER=${DBUSER}_pad
    PADPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`
    # clone etherpad-lite stable branch (=master) from github
    git clone -b master https://github.com/ether/etherpad-lite.git ${PADPATH} | tee -a $DB_SETUPLOG
    chown -R ${DBUSER}:${DBUSER} ${PADPATH} | tee -a $DB_SETUPLOG
    echo -e "\n---- Create etherpad-lite db role $PADUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${PADUSER}' WITH NOSUPERUSER LOGIN PASSWORD '\'${PADPW}\''"' | tee -a $DB_SETUPLOG
    # Create the owncloud database (utf8)
    # Create the etherpad database (utf8)
    echo -e "Create DB for etherpad-lite: ${PADDB} Owner: ${PADUSER}"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE DATABASE '${PADDB}' WITH OWNER '${PADUSER}' ENCODING '\'UTF8\''" ' | tee -a $DB_SETUPLOG
    #
    # etherpad-lite CONFIG file
    echo -e "Create etherpad config file"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!DBNAME!'"$DBNAME"'!g
        s!PADDB!'"$PADDB"'!g
        s!PADUSER!'"$PADUSER"'!g
        s!PADPW!'"$PADPW"'!g
        s!ETHERPADKEY!'"$ETHERPADKEY"'!g
        s!PADLOG!'"$PADLOG"'!g
        }' ${INSTANCE_PATH}/TOOLS/etherpad.conf > ${PADCONF} | tee -a $DB_SETUPLOG
    chown root:root ${PADCONF}
    chmod ugo=r ${PADCONF}
    #
    # etherpad-lite INIT file
    echo -e "Create etherpad init file and start service"
    /bin/sed '{
        s!DBUSER!'"$DBUSER"'!g
        s!PADPATH!'"$PADPATH"'!g
        s!DBNAME!'"$DBNAME"'!g
        s!PADCONF!'"$PADCONF"'!g
        }' ${INSTANCE_PATH}/TOOLS/etherpad.init > ${PADINIT} | tee -a $DB_SETUPLOG
    chown root:root ${PADINIT}
    chmod ugo=rx ${PADINIT}
    ln -s ${PADINIT} /etc/init.d/${DBNAME}-pad | tee -a $DB_SETUPLOG
    update-rc.d ${DBNAME}-pad start 20 2 3 5 . stop 80 0 1 4 6 . | tee -a $DB_SETUPLOG
    service ${DBNAME}-pad start
    echo -e "---- Setup etherpad-Lite DONE"

    # ----- Setup owncloud
    echo -e "\n---- Setup owncloud"
    OWNCLOUDPATH=${DBPATH}/owncloud
    CLOUDDB=${DBNAME}_cloud
    CLOUDUSER=${DBUSER}_cloud
    CLOUDPW=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 8 | head -1`
    # download owncloud and create directory owncloud with tar
    cd ${DBPATH}
    wget https://download.owncloud.org/community/owncloud-7.0.2.tar.bz2 -O ${DBPATH}/owncloud-7.0.2.tar.bz2
    tar -xjf ${DBPATH}/owncloud-7.0.2.tar.bz2 -C ${DBPATH}
    mkdir ${OWNCLOUDPATH}/data | tee -a $DB_SETUPLOG
    chown -R ${DBUSER}:${DBUSER} ${OWNCLOUDPATH} | tee -a $DB_SETUPLOG
    chown -R www-data:www-data ${OWNCLOUDPATH}/config/ ${OWNCLOUDPATH}/apps/ ${OWNCLOUDPATH}/data/ | tee -a $DB_SETUPLOG
    # Create owncloud db user
    echo -e "\n---- Create owncloud db role: $CLOUDUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${CLOUDUSER}' WITH NOSUPERUSER LOGIN PASSWORD '\'${CLOUDPW}\''"' | tee -a $DB_SETUPLOG
    # Create the owncloud database (utf8)
    echo -e "\n---- Create owncloud DB: $CLOUDDB"
    echo -e "Create DB for owncloud: ${CLOUDDB} Owner: ${CLOUDUSER}"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE DATABASE '${CLOUDDB}' WITH OWNER '${CLOUDUSER}' ENCODING '\'UTF8\''" ' | tee -a $DB_SETUPLOG
    #
    # ----- Configure owncloud
    OWNCLOUDCONFIGFILE="${DBPATH}/${CLOUDDB}-autoconfig.php"
    echo -e "Create Configuration for owncloud and link it to owncloud config dir"
    echo "<?php" >> ${OWNCLOUDCONFIGFILE}
    echo     '$AUTOCONFIG = array (' >> ${OWNCLOUDCONFIGFILE}
    echo      "'dbtype' => 'pgsql'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'dbname' => '${CLOUDDB}'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'dbuser' => '${CLOUDUSER}'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'dbpass' => '${CLOUDPW}'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'dbhost' => 'localhost'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'dbtableprefix' => ''," >> ${OWNCLOUDCONFIGFILE}
#    echo    "'trusted_domains' =>" >> ${OWNCLOUDCONFIGFILE}
#    echo    "array (" >> ${OWNCLOUDCONFIGFILE}
#    echo       "0 => 'cloud.${DOMAIN_NAME}'," >> ${OWNCLOUDCONFIGFILE}
#    echo     ")," >> ${OWNCLOUDCONFIGFILE}
    echo     "'directory' => '${OWNCLOUDPATH}/data'," >> ${OWNCLOUDCONFIGFILE}
#    echo     "'version' => '7.0.2.1'," >> ${OWNCLOUDCONFIGFILE}
#    echo     "'installed' => 'true'," >> ${OWNCLOUDCONFIGFILE}
#    echo     "'mail_smtpmode' => 'php'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'adminlogin' => 'cloudadmin'," >> ${OWNCLOUDCONFIGFILE}
    echo     "'adminpass' => 'cloudadmin#1'," >> ${OWNCLOUDCONFIGFILE}
    echo     ");" >> ${OWNCLOUDCONFIGFILE}
#    ${OWNCLOUDCONFIGFILE} | tee -a /tmp/test.log
    ln -s ${OWNCLOUDCONFIGFILE} ${OWNCLOUDPATH}/config/autoconfig.php
    chown root:root ${OWNCLOUDCONFIGFILE}
    chmod ugo=rx ${OWNCLOUDCONFIGFILE}
    echo -e "---- Setup owncloud DONE"

    # ----- Setup cron Logrotate for all Logfiles
    DBLOGROT="${DBPATH}/${DBNAME}-logrotate.conf"
    echo -e "${DBLOGPATH}/*.log" > ${DBLOGROT}
    echo -e "{"                  >> ${DBLOGROT}
    echo -e "   rotate 53"       >> ${DBLOGROT}
    echo -e "	weekly"          >> ${DBLOGROT}
    echo -e "   notifempty"      >> ${DBLOGROT}
    echo -e "   copytruncate"    >> ${DBLOGROT}
    echo -e "   compress"        >> ${DBLOGROT}
    echo -e "   delaycompress"   >> ${DBLOGROT}
    echo -e "}"                  >> ${DBLOGROT}
    ln -s ${DBLOGROT} /etc/logrotate.d/${DBNAME}

    # ----- Create backup script and Setup cron job for backup script
    DBBACKUPSCRIPT="${DBPATH}/${DBNAME}-backup.sh"
    echo -e "Create database backup script and link to cron daily"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!INSTANCE_PATH!'"$INSTANCE_PATH"'!g
        s!DBNAME!'"$DBNAME"'!g
        s!DBBACKUPPATH!'"$DBBACKUPPATH"'!g
        s!BACKUPFILE!'"$DBBACKUPPATH/$DBNAME"'!g
        s!BACKUPTYPE!'"odoo-backup-zip"'!g
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${DBBACKUPSCRIPT} | tee -a $DB_SETUPLOG
    chown root:root ${DBBACKUPSCRIPT}
    chmod ugo=rx ${DBBACKUPSCRIPT}
    ln -s ${DBBACKUPSCRIPT} /etc/cron.daily/${DBNAME}-backup | tee -a $DB_SETUPLOG

    # ----- Create backup script for PAD and Setup cron job for backup script
    PADDBBACKUPSCRIPT="${DBPATH}/${PADDB}-backup-pad.sh"
    echo -e "Create PAD database backup script and link to cron daily"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!INSTANCE_PATH!'"$INSTANCE_PATH"'!g
        s!DBNAME!'"$PADDB"'!g
        s!DBBACKUPPATH!'"$DBBACKUPPATH"'!g
        s!BACKUPFILE!'"$DBBACKUPPATH/$PADDB"'!g
        s!BACKUPTYPE!'"pad-backup-sql"'!g
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${PADDBBACKUPSCRIPT} | tee -a $DB_SETUPLOG
    chown root:root ${PADDBBACKUPSCRIPT}
    chmod ugo=rx ${PADDBBACKUPSCRIPT}
    ln -s ${PADDBBACKUPSCRIPT} /etc/cron.daily/${PADDB}-backup-pad | tee -a $DB_SETUPLOG

    # ----- Create backup script for OWNCLOUD and Setup cron job for backup script
    CLOUDDBBACKUPSCRIPT="${DBPATH}/${CLOUDDB}-backup-owncloud.sh"
    echo -e "Create PAD database backup script and link to cron daily"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!INSTANCE_PATH!'"$INSTANCE_PATH"'!g
        s!DBNAME!'"$CLOUDDB"'!g
        s!DBBACKUPPATH!'"$DBBACKUPPATH"'!g
        s!BACKUPFILE!'"$DBBACKUPPATH/$CLOUDDB"'!g
        s!BACKUPTYPE!'"owncloud-backup-sql"'!g
        s!DBPATH!'"${DBPATH}"'!g
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${CLOUDDBBACKUPSCRIPT} | tee -a $DB_SETUPLOG
    chown root:root ${CLOUDDBBACKUPSCRIPT}
    chmod ugo=rx ${CLOUDDBBACKUPSCRIPT}
    ln -s ${CLOUDDBBACKUPSCRIPT} /etc/cron.daily/${CLOUDDB}-backup-owncloud | tee -a $DB_SETUPLOG

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODENEWDB DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    echo -e "\nAfter database install you should follow these steps:"
    echo -e ""
    echo -e "1) Open http://$DOMAIN_NAME with USER: \"admin\" PASSWORD: \"adminpw\")."
    echo -e "2) Install the addon base_config in your new DB $DBNAME."
    echo -e "3) During install of base_config select austrian-chart-of-account and 20%-Mwst and 20%-Vst."
    echo -e "4) After install set time period to month for HR."
    echo -e "\n5) Enable Colaborative Pads at URL http://pad.${DOMAIN_NAME} (PWD: $SUPER_PASSWORD)"
    echo -e "   You will find the API-KEY at: ${PADPATH}/APIKEY.txt"
    echo -e "   ATTENTION: First start of etherpad-lite takes a long time. Be patient - APIKEY will show up after first start!"
    echo -e "\n6) Start owncloud at URL http://cloud.${DOMAIN_NAME} with cloudadmin cloudadmin#1 and change cloudadmin password"
    echo -e "   ATTENTION: Make sure cloud.${DOMAIN_NAME} is resolvable via DNS on the server. (dig cloud.${DOMAIN_NAME})!"
    echo -e "\n Optional:"
    echo -e "1) Set Company Details"
    echo -e "2) Set Timezone, Signature and Mail-Options for Admin and Default user"
    echo -e "3) Set RealTime Warehouse Accounts for Product Categories: Maybe obsolete in v8 new wms?"
    echo -e "\n SSH to this server with \"ssh ${DBUSER}@${DOMAIN_NAME}\" PASSWORD: ${LINUXPW}\n"
    exit 0
fi


# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh updateinst  {TARGET_BRANCH} {DATABASE_NAME}
# in diesem teil sollten die Updates am Kundenserver durchgeführt werden und alle kundendb's upgedated werden
# ---------------------------------------------------------------------------------------
MODEUPDATEINST="$ odoo-tools.sh updateinst {TARGET_BRANCH} check|dbname|all"
if [ "$SCRIPT_MODE" = "updateinst" ]; then

    UPDATELOGFILE="${DBPATH}/${SCRIPT_MODE}--${TARGET_BRANCH}--`date +%Y-%m-%d__%H-%M`.log"
    DATABASE_NAME=%3
    TARGET_BRANCH=%2
    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"
    REVERTUPDATELOGFILE="${DBPATH}/${SCRIPT_MODE}--${TARGET_BRANCH}--UPDATELOGFILE--`date +%Y-%m-%d__%H-%M`.log"
    UPGRADEPATHCONFIG="${REPOPATH}/TOOLS/upgradepathconfig.txt"

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATEINST"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 3 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly three arguments!"
        exit 2
    fi
    #safe status infos for revert and log
    git log -1 --pretty="%H" |
    while read line; do
        echo "[local CommitID = ] $line" | tee -a $UPDATELOGFILE $REVERTUPDATELOGFILE
    done

    if [ "$DATABASE_NAME" = "all" ]; then
        #get all running Databases DATABASES_RUNNING = ($(ps -ef |grep "o8_$TARGET_BRANCH_*" -v grep "o8_$TARGET_BRANCH_*" )
        #DATABASE_RUNNING=( `ps -ef|grep "o8_${TARGET_BRANCH}" |grep grep --invert-match|awk '{printf $2;printf "\n"; }'` )
        # CHECK WHICH INSTACES ARE RUNNING
        DATABASE_RUNNING=($(ps -ef|grep "openerp-server*" |awk '{printf $13;printf "\n"; }')) #TODO: check aber auch ALLE Prostgres Prozesse
        for i in "${DATABASE_RUNNING[@]}";
        do #store running databases and log do
                :
             echo "Running DB: " $i >> $UPDATELOGFILE $REVERTUPDATELOGFILE
        done
        echo "get latest status of remote github...." >> $UPDATELOGFILE
        git fetch | tee -a $UPDATELOGFILE $REVERTUPDATELOGFILE
        if [ -n "$(git status --porcelain)" ]; then # wenn es eine differenz gibt
            echo "do parsing and git checks whats up..." >> $UPDATELOGFILES
            git status | grep
            exit 2
            #TODO: noch zu überlegen was hier alles zu tun ist
            #Todo: Branch Check
            #TODO: git diff --exit-code --> 0 oder 1 --> CHANGESMADE=1 check lokale unstaged changes
            #TODO: git diff --cached --exit-code --> CHANGESMADE=2 check lokale staged aber nicht commited
            #TODO: git ls-files --other --exclude-standard --directory --> finde eventuelle PYC files oder sonst was .... weitere überprüfung notwendig
            #Todo: oder check gitignore löschen der PYC files wenn nicht im repo
            #EXAMPLE write  function for this and call whereever needed check_git_needs()
            ##!/bin/sh

            # LOCAL=$(git rev-parse @)
            #REMOTE=$(git rev-parse @{u})
            #BASE=$(git merge-base @ @{u})

            #if [ $LOCAL = $REMOTE ]; then
            #    echo "Up-to-date"
            #elif [ $LOCAL = $BASE ]; then
            #    echo "Need to pull"
            #elif [ $REMOTE = $BASE ]; then
            #    echo "Need to push"
            #else
            #    echo "Diverged"
            #fi

        else # wenn alles ok ist kann man das update machen FALL 1
            echo "no local changes found this branch will be updated, git pull..." >> $UPDATELOGFILE
            #TODO: check if i can reversibly call odoo-tools.sh
            odoo-tools.sh maintenancemode "all" "enable" | tee -a $UPDATELOGFILE
            INIT4REACHED=0 #init 4 ist solange nicht erreicht solange ein process lauft
            WAITINGCOUNTER=0
            while [ $INIT4REACHED != 1 ]; do
                DATABASE_RUNNING=($(ps -ef|grep "openerp-server*" |awk '{printf $13;printf "\n"; }'))
                inarray=$(echo ${DATABASE_RUNNING[@]} | grep -o "" | wc -w)
                if [ $inarray -ne 0 ]; then
                    sleep 1
                    WAITINGCOUNTER=$[$WAITINGCOUNTER +1]
                    echo "waiting...."
                    if [ $WAITINGCOUTNER -eq 20 ]; then #warte max 20 sec
                        echo "check running process and kill process"
                        #Todo: kill processes still running and postgres databases to that process
                        #downfahren etherpad und owncloud
                        break
                    fi
                else
                    INIT4REACHED=1
                fi
            done
            # --------------- Todo: write this into a function called local maintainenancemode() END
            #Todo: backup databases check stuff with BARMAN Server more efficient BAckup and REVERT ABER ALLE
            #Todo: start odoo_tools maintainenance all|database {start|stop}
            #Todo: backup and restore use odoo tool
            #TODO: another VMWARE Snapshot to have all OFFLINE
            #Todo: garantieren das das Backup Funktioniert --> restore psql dryrun restore run check oder in ein fak_backup db ....
            #Todo: update tools for singular BACKUP of one DATABASE rewrite o8_repo_..... only nginx config file use backup.sh tool
            #todo: restore.sh dry run erweitern
            #--------------------------- git checks
            #check $UPGRADEPATHCONFIGremote and consider Todos
            #compare local $UPGRADEPATHCONFIGlocal <> $UPGRADEPATHCONFIGremote
            #write remoteconfig file into a local store log to have the positions where to go
            #find start position mylocalrepoID == linepostion-commitIDremotefile
            #commitIDtarget = last commit entry from $UPGRADEPATHCONFIGremotefile
            #while mylocalrepoID != $commitIDtarget do
                #while readline $UPGRADEPATHCONFIGremotefile Todo: == ZERO || mylocalrepoID != $commitIDtarget do
                    #commitIDtarget = commitID from next line in remotefile
                #done
                #Todo: $INSTANCE_PATH/git pull commitIDtarget | tee -a $UPDATELOGFILE
                #Todo: git pull all NEU weil wir das neu beschlossen haben wegen des zusammenfaassens der befehle
                #Todo: echo "UpgradePositioncommitID" $commitIDtarget >> $REVERTUPDATELOGFILE
                #Todo: check config file Todo: and get parameter from appropriate line
                #Todo: get $DATABASE_RUNNING= Running DB's from $REVERTUPDATELOGFILE awk second param
                #Todo: get parameters to work on --> SPLIT line of config FILE into
                #odooserver -- gitsuff -- reservedpython -- reservedpostgresql
                #Todo: split line to these parameters
                #for i in "${DATABASE_RUNNING[@]}";
                #do
                #    :
                #    #todo: if abfrage für die optionsbereiche im config file
                #    #if [ todo: == ZERO ]; then
                #        echo "nothing to do"
                #    #else
                #        if [ $odooserver != "" ]; then
                #            paramcounter=0
                #            while readline ${odooserver{@}}; do
                #                git ${odooserver[$paramcounter]} #todo: checks if command successfully
                #                paramcounter+=1
                #            done
                #        else
                #        if [ $gitstuff != "" ]; then
                #            paramcounter=0
                #            while readline ${gitstuff{@}}; do
                #                git ${odooserver[$paramcounter]} #todo: checks if command successfully
                #                paramcounter+=1
                #            done
                #        else
                #        if [ $reservedpython != "" ]; then
                #            paramcounter=0
                #            while readline ${reservedpython{@}}; do
                #                python ${reservedpython[$paramcounter]} #todo: checks if command successfully
                #                paramcounter+=1
                #            done
                #        else
                #        if [ $reservedpostgresql != "" ]; then
                #            paramcounter=0
                #            while readline $reservedpostgresql{{@}}; do
                #                postgresql ${reservedpostgresql[$paramcounter]} #todo: checks if command successfully
                #                paramcounter+=1
                #            done
                #        else
                #        fi
                #    fi
                #done
            #done
            #Todo: if [ -n "$(git status --porcelain)" ]; then # alles gut
            #Todo: schreibe logfile mit Status
            #$INSTANCE_PATH/git status | tee -a $UPDATELOGFILE
            #update finished all works
            #disable maintenance mode
            odoo-tools.sh maintenancemode $TARGET_BRANCH "disable"
            #mv $MAINTENANCEMODESWITCHERON $MAINTENANCEMODESWITCHEROFF | tee -a $UPDATELOGFILE
        fi
        #update special DATABASES on this server
    else
        if [ "$DATABASE_NAME" = "" ]; then
            echo "nix" #do only updatedev files but stopping stuff aso.... maybe write a function for some basic tests
        fi
    fi
    # TODO: Stop all o8_INSTANCENAME_* Services (remember all that where running!!!)
    # TODO: Stop all o8_INSTANCENAME PAD SERVICES (because etherpad-lite is maybe updated as well)
    # ATTENTION: Do not stop aeroo service (important if more than one instance is on the server)
    # Todo: git fetch, git checkout master, git pull, git checkout INSTANCENAME, git rebase
    # todo: start all pad services
    # todo: start the odoo services (only those who where running before)

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATEINST DONE"
    echo -e "\n--------------------------------------------------------------------------------------------------------"
fi

# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh updatecorebranch {TARGET_BRANCH} {DATABASE_NAME}
# ---------------------------------------------------------------------------------------
MODEUPDATECORE="$ odoo-tools.sh updatecorebranch {TARGET_BRANCH} {DATABASE_NAME}"
if [ "$SCRIPT_MODE" = "updatecorebranch" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATECORE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly two arguments!"
        exit 2
    fi
    #ERSTER SCHRITT für das UPDATE des CORE
    #vielleicht brauch ich den teil nicht aber mit diesem teil soll sonst das Core Update Lokal durchgeführt werden

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATECORE DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
fi

MAINTENANCEMODE="$ odoo-tools.sh maintenancemode {TARGET_BRANCH} dbname|all {SWITCHER} enable|disable"
if [ "$SCRIPT_MODE" = "maintenancemode" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MAINTENANCEMODE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly two arguments!"
        exit 2
    fi
    MAINTENANCEMODESWITCHERON="/usr/share/nginx/html/maintenance_ein"
    MAINTENANCEMODESWITCHEROFF="/usr/share/nginx/html/maintenance_aus"
    DBONLYMAINTENANCEMODESWITCHERON="$INSTANCE_PATH/maintenance_ein"
    DBONLYMAINTENANCEMODESWITCHEROFF="$INSTANCE_PATH/maintenance_aus"
            #set Nginx in maintenance mode --> just rename /usr/share/nginx/html/maintenance_aus --> /usr/share/nginx/html/maintenance_ein
            #a rule in nginx.conf will check if the maintenance file is set or not
            # enable Maintenance mode
            # --------------- Todo: write this into a function called local maintainenancemode() {start stop} BEGIN
            #TODO: create two ways single and ALL all switches nginx defaut
            if [ "$TARGET" = "all" ]; then
                    if [ -e "$MAINTENANCEMODESWITCHEROFF" ]; then
                        mv $MAINTENANCEMODESWITCHEROFF $MAINTENANCEMODESWITCHERON | tee -a $UPDATELOGFILE #check
                    else
                        touch $MAINTENANCEMODESWITCHERON #if file exists error occures but status is now correct
                    fi
            else
                #Todo: move nginx witcher file in target db only but first change Install script to add nginx config to database nginx config not default
                # ${TARGET_BRANCH}
                if [ -e "$DBONLYMAINTENANCEMODESWITCHEROFF" ]; then
                    mv $DBONLYMAINTENANCEMODESWITCHEROFF $DBONLYMAINTENANCEMODESWITCHERON | tee -a $UPDATELOGFILE #check
                else
                    touch $DBONLYMAINTENANCEMODESWITCHERON #if file exists error occures but status is now correct
                fi

            fi
            #init 4 also stops
            service nginx stop
            #ONLY STOPPING NGINX NO INSTANCE OR ANYTHING ELSE init 4 | tee -a $UPDATELOGFILE # stop all running processes postgres, openerp, pads, clouds
            sleep 10 #wait for processes to be shut down
            #its a good idea to restart nginx this time staled processes aso are cleared now ...
            if [ "$(pgrep nginx)" = "" ]; then
                service nginx start
            else
                killall nginx
                service nginx start
            fi
    #ERSTER SCHRITT setzt die jeweilige instanz von Nginx in den maintenance mode oder den ganzen server
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MAINTENANCEMODE DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
fi

# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh backup      {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME}
# ---------------------------------------------------------------------------------------
MODEBACKUP="$ odoo-tools.sh backup      {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME}"
if [ "$SCRIPT_MODE" = "backup" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEBACKUP"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly four arguments!"
        exit 2
    fi

    # TODO: check or create INSTANCE/DATABASE/BACKUP folder
    # Todo: CD to BACKUP folder
    # Todo: create backup with dbname--DATE.zip with DATE in Format 2014-12-30--24-59


    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEBACKUP DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
fi

# ---------------------------------------------------------------------------------------
# $ odoo-tools.sh restore     {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {BACKUPFILE_NAME}
# ---------------------------------------------------------------------------------------
MODERESTORE="$ odoo-tools.sh restore     {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {BACKUPFILE_NAME}"
if [ "$SCRIPT_MODE" = "restore" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODERESTORE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly five arguments!"
        exit 2
    fi

    # Todo: Check if BACKUPFILE_NAME exists and is readable
    # Todo: Try to restore BACKUPFILE_NAME to DBNAME_restoretest
        # If success Todo: Remove DB DBNAME_restoretest
    # Todo: Backup DBNAME
        # check size, and if restoreabel - so restore and if success remove db again :)
        # If success Todo: Remove DBNAME
        # Todo: Restore BACKUPFILE_NAME to DBNAME
            # If success restart DBNAME service

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODERESTORE DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
fi

# ---------------------------------------------------------
# Script HELP
# ---------------------------------------------------------
echo -e "\n----- SCRIPT USAGE -----"
echo -e "$ odoo-tools.sh {prepare|setup|newdb|dupdb|deploy|backup|restore}\n"
echo -e "$ $MODEPREPARE"
echo -e "$ $MODESETUP"
echo -e "$ $MODENEWDB"
echo -e "$ odoo-tools.sh upgradeinst {TARGET_BRANCH} check|dbname|all"
echo -e "$ $MODEUPDATEINST"
echo -e "$ odoo-tools.sh maintenancemode {all|dbname} {enable|disable}"
echo -e "$ $MAINTENANCEMODE"
echo -e "TODO: $ odoo-tools.sh dupdb {BRANCH} {SOURCE_SUPER_PASSWORD} {SOURCE_DBNAME} {TARGET_DBNAME} {TARGET_DOMAIN}"
echo -e "TODO: $ odoo-tools.sh deployaddon {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "TODO: $MODEBACKUP"
echo -e "TODO: $MODERESTORE"
echo -e "------------------------\n"
