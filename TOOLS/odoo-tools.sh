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
    if [ -w "${SETUP_LOG}" ] ; then
        echo -e "Setup log file: ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
    else
        if  touch ${SETUP_LOG} 2>&1>/dev/null; then
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

    if ! egrep -i "LANG=.*UTF-8" /etc/default/locale >> ${SETUP_LOG}; then
        echo 'LANG="en_US.UTF-8"' >> /etc/default/locale
        locale_set=true
    fi

    if ! egrep -i "LANGUAGE=...+" /etc/default/locale >> ${SETUP_LOG}; then
        echo 'LANGUAGE="en_US.UTF-8"' >> /etc/default/locale
        locale_set=true
    fi
    locale-gen en_US.UTF-8 >> ${SETUP_LOG}
    locale-gen de_AT.UTF-8 >> ${SETUP_LOG}
    update-locale >> ${SETUP_LOG}
    if [ "$locale_set" = true ]; then
        echo "ERROR: Wrong locale settings (NOT UTF8)! Please logout completely, login and try again!"
        exit 3
    fi

    # ----- Update Server
    echo -e "\n----- Update Server"
    #sudo sed -i -e 's/archive.ubuntu.com\|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
    apt-get update >> ${SETUP_LOG}
    apt-get upgrade -y >> ${SETUP_LOG}
    echo -e "----- Update Server Done"

    # ----- Install Basic Packages
    echo -e "\n----- Install Basic Packages"
    apt-get install ssh wget sed git git-core gzip curl python libssl-dev libxml2-dev libxslt-dev libxslt1-dev \
        build-essential gcc mc bzr lptools make nodejs nodejs-dev nodejs-legacy pkg-config npm gdebi -y >> ${SETUP_LOG}
    echo -e "----- Install Basic Packages Done"

    # ----- Install postgresql
    echo -e "\n----- Install postgresql"
    apt-get install postgresql postgresql-server-dev-9.3 libpq-dev -y >> ${SETUP_LOG}
    update-rc.d -f postgresql remove
    update-rc.d postgresql start 19 2 3 5 . stop 81 0 1 4 6 . >> ${SETUP_LOG}
    service postgresql restart | tee -a ${SETUP_LOG}
    echo -e "----- Install postgresql Done"

    # ----- Install nginx
    echo -e "\n----- Install nginx"
    apt-get remove apache2 apache2-mpm-event apache2-mpm-prefork apache2-mpm-worker -y >> ${SETUP_LOG}
    apt-get install nginx -y >> ${SETUP_LOG}
    update-rc.d -f nginx remove
    update-rc.d nginx start 20 2 3 5 . stop 80 0 1 4 6 . >> ${SETUP_LOG}
    service nginx restart | tee -a ${SETUP_LOG}
    touch /usr/share/nginx/html/maintenance_aus.html >>$SETUP_LOG
    echo -e "----- Install nginx Done"

    # ----- Install push-to-deploy
    echo -e "\n----- Install pushtodeploy"
    npm install push-to-deploy -y >> ${SETUP_LOG}
    echo -e "----- Install pushtodeploy Done"

    # ----- Install Python Packages
    echo -e "\n----- Install Python Apt Packages"
    apt-get install libldap2-dev libsasl2-dev python-pip python-virtualenv python-dev python-software-properties python-pychart \
        python-genshi python-pyhyphen python-ldap -y >> ${SETUP_LOG}
    pip install pyserial >> ${SETUP_LOG}
    pip install qrcode >> ${SETUP_LOG}
    pip install --pre pyusb >> ${SETUP_LOG}
    echo -e "\n----- Install Python Apt Packages DONE"

    # ----- Install Wkhtmltopdf 0.12.1
    echo -e "\n----- Install Wkhtmltopdf 0.12.2.1"
    if wkhtmltopdf -V | grep "wkhtmltopdf.*12.2.*" 2>&1>/dev/null; then
      echo -e "\nWkhtmltopdf 0.12.2.x seems to be installed! Skipping installation!\n"
    else
        apt-get install libjpeg-dev libjpeg8-dev libtiff5-dev vflib3-dev pngtools libpng3 gdebi -y >> ${SETUP_LOG}
        apt-get install xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic -y >> ${SETUP_LOG}

        cd ${REPO_SETUPPATH}
        #wget http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb >> ${SETUP_LOG}
        #dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb >> ${SETUP_LOG}
        #cp /usr/local/bin/wkhtmltopdf /usr/bin >> ${SETUP_LOG}
        #cp /usr/local/bin/wkhtmltoimage /usr/bin >> ${SETUP_LOG}

        wget http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb
        gdebi -n wkhtmltox-0.12.2.1_linux-trusty-amd64.deb >> ${SETUP_LOG}
        rm wkhtmltox-0.12.2.1_linux-trusty-amd64.deb >> ${SETUP_LOG}
        ln -s /usr/local/bin/wkhtmltopdf /usr/bin/
        ln -s /usr/local/bin/wkhtmltoimage /usr/bin/

        apt-get install flashplugin-nonfree -y >> ${SETUP_LOG}
        pip install git+https://github.com/qoda/python-wkhtmltopdf.git >> ${SETUP_LOG}
    fi
    echo -e "\n----- Install Wkhtmltopdf 0.12.2.1 DONE"

    # ----- Install python libs from requirements.txt
    echo -e "\n----- Install python libs from requirements.txt"
    wget -O - ${GITRAW}/TOOLS/requirements.txt | grep -v '.*#' > ${REPO_SETUPPATH}/requirements.txt
    while read line; do
        if pip install ${line} >> ${SETUP_LOG}; then
            echo -e "Installed: ${line}"
        else
            echo -e "\n\nWARNING Install FAILED: ${line} !\n\n" | tee -a ${SETUP_LOG}
        fi
        if pip freeze | grep ${line} >> ${SETUP_LOG}; then
            echo -e "PackageOK: ${line} "
        else
            echo -e "\n\nWARNING: Package ${line} missing!\n\n" | tee -a ${SETUP_LOG}
        fi
    done < ${REPO_SETUPPATH}/requirements.txt
    echo -e "----- Install python libs from requirements.txt Done"

    # ----- Make sure Pil is used not Pillow
    echo -e "\n----- Make sure Pil is used and not Pillow"
    apt-get remove pil pillow -y >> ${SETUP_LOG}
    pip uninstall pil
    pip uninstall pillow
    apt-get install libjpeg-dev libfreetype6-dev zlib1g-dev libtiff4 libtiff4-dev python-libtiff -y >> ${SETUP_LOG}
    pip install Pillow==2.5.1 --upgrade

    # ----- Install Packages for AerooReports
    echo -e "\n----- Install Packages for AerooReports"
    # ATTENTION: LibreOffice-Python 2.7 Compatibility Script Author: Holger Brunn (https://gist.github.com/hbrunn/6f4a007a6ff7f75c0f8b)
    # Maybe this is needed because of python-uno bridge?!? - We will see when we start the test for aeroo reports in v8
    easy_install uno
    apt-get install ure uno-libs3 unoconv graphviz ghostscript\
                    libreoffice-core libreoffice-common libreoffice-base libreoffice-base-core \
                    libreoffice-draw libreoffice-calc libreoffice-writer libreoffice-impress \
                    python-cupshelpers hyphen-de hyphen-en-us -y >> ${SETUP_LOG}
    echo -e "\n\nInstall Aeroolib"
    if pip freeze | grep aeroolib ; then
        echo -e "\n\nWARNING: Aeroolib seems to be already installed!" | tee -a ${SETUP_LOG}
        echo -e "Please upgrade manually if needed!"
        echo -e "Aeroolib has to be at least aeroolib==1.2.0 to work with ${REPONAME}\n\n"
    else
        if [ -d ${REPO_SETUPPATH}/aeroolib ]; then
            echo -e "Do not clone aeroolib from github since directory ${REPO_SETUPPATH}/aeroolib exists ."
        else
            echo -e "Clone aeroolib from github."
            git clone --depth 1 --single-branch https://github.com/aeroo/aeroolib.git ${REPO_SETUPPATH}/aeroolib >> ${SETUP_LOG}
        fi
        cd ${REPO_SETUPPATH}/aeroolib >> ${SETUP_LOG}
        python ${REPO_SETUPPATH}/aeroolib/setup.py install | tee -a ${SETUP_LOG}
        if pip freeze | grep aeroolib ;  then
            echo -e "\nAeroolib is successfully installed!\n"
        else
            echo -e "\nWARNING: Could not install aeroolib\n"
        fi
        cd ${REPO_SETUPPATH} >> ${SETUP_LOG}
        echo -e "\nInstall Aeroo LibreOffice Service to init.d as service aeroo"
        wget -O - ${GITRAW}/TOOLS/aeroo.init > ${REPO_SETUPPATH}/aeroo.init
        chmod ugo=rx ${REPO_SETUPPATH}/aeroo.init >> ${SETUP_LOG}
        ln -s ${REPO_SETUPPATH}/aeroo.init /etc/init.d/aeroo >> ${SETUP_LOG}
        update-rc.d -f aeroo remove
        update-rc.d aeroo start 20 2 3 5 . stop 80 0 1 4 6 . >> ${SETUP_LOG}
        service aeroo stop
        service aeroo start
    fi
    echo -e "----- Install Packages for AerooReports Done"

    # ----- Install Packages for Etherpad Lite
    echo -e "\n----- Install Packages for Etherpad Lite"
    apt-get install abiword -y >> ${SETUP_LOG}
    echo -e "----- Install Packages for Etherpad Lite Done"

    # ----- Less compiler needed by Odoo 8 Website - added from https://gist.github.com/rm-jamotion/d61bc6525f5b76245b50
    echo -e "\n----- Install less compiler"
    hash -r
    npm install -g less less-plugin-clean-css -y && ln -s /usr/bin/nodejs /usr/bin/node >> ${SETUP_LOG}
    echo -e "----- Install less compiler DONE"

    # ----- Install packages for owncloud
    echo -e "\n----- Install packages for owncloud"
    apt-get install php5-fpm -y >> ${SETUP_LOG}
    apt-get install php5-cgi php5-pgsql php5-gd php5-curl php5-intl php5-mcrypt php5-ldap php5-gmp php5-imagick \
                    libav-tools php5-readline -y >> ${SETUP_LOG}
    # --- Make sure PHP-FPM is listening on unix socket and not on IP!
    if /bin/grep -q "listen = 127.0.0.1:9000" ${FPMCONFIGPATH} ; then
        sed -i "s|listen = 127.0.0.1:9000|listen = /var/run/php5-fpm.sock|g" ${FPMCONFIGPATH}
    fi
    update-rc.d -f apache2 disable >> ${SETUP_LOG}
    echo -e "\n----- Install packages for owncloud done"

    # ----- GEO IP DB for odoo 8
    echo -e "\n----- Install GEO-IP-DB"
    wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
    gunzip GeoLiteCity.dat.gz >> ${SETUP_LOG}
    mkdir /usr/share/GeoIP/ >> ${SETUP_LOG}
    mv GeoLiteCity.dat /usr/share/GeoIP/ >> ${SETUP_LOG}
    echo -e "----- Install GEO-IP-DB DONE"


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
    echo -e "\$1 Script Mode                    :  $SCRIPT_MODE" | tee -a ${INSTANCE_SETUPLOG}
    echo -e "\$2 Target Branch                  :  $TARGET_BRANCH" | tee -a ${INSTANCE_SETUPLOG}
    echo -e ""
    echo -e "Instance Setuplog File            :  ${INSTANCE_SETUPLOG}" | tee -a ${INSTANCE_SETUPLOG}
    echo -e ""
    echo -e "Instance Branch Name              :  $TARGET_BRANCH" | tee -a ${INSTANCE_SETUPLOG}
    echo -e "Instance Base Directory           :  $INSTANCE_PATH" | tee -a ${INSTANCE_SETUPLOG}
    echo -e "Instance LINUX User               :  $TARGET_BRANCH" | tee -a ${INSTANCE_SETUPLOG}
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
        ${SOURCE_REPO} ${INSTANCE_PATH} | tee -a ${INSTANCE_SETUPLOG}
    cd ${INSTANCE_PATH} >> ${INSTANCE_SETUPLOG}
    git branch ${TARGET_BRANCH} >> ${INSTANCE_SETUPLOG}
    git checkout ${TARGET_BRANCH} >> ${INSTANCE_SETUPLOG}
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
    useradd -m -s /bin/bash ${TARGET_BRANCH} | tee -a ${INSTANCE_SETUPLOG}

    # ----- Set Linux Rights
    chown -R ${TARGET_BRANCH}:${TARGET_BRANCH} ${INSTANCE_PATH} >> ${INSTANCE_SETUPLOG}
    chmod 755 ${INSTANCE_PATH} >> ${INSTANCE_SETUPLOG}

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
# $ odoo-tools.sh newdb {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME} {DATABASE_NAME} [CUADDONSREPONAME]
# ---------------------------------------------------------------------------------------
MODENEWDB="odoo-tools.sh newdb       {TARGET_BRANCH} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME} [CUADDONSREPONAME]"
MODEDUPDB="odoo-tools.sh duplicatedb {TARGET_BRANCH} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME} {DATABASE_TEMPLATE}"
if [ "$SCRIPT_MODE" = "newdb" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODENEWDB"
    echo -e "--------------------------------------------------------------------------------------------------------"
    echo -e "DATABASE_NAME MUST BE the unique customer number E.g.: pfot, ahch, dadi, ... "
    echo -e "DATABASE_NAME will be used for the default domains! E.g. for ahch:"
    echo -e "    ahch.datadialog.net aswidget.ahch.datadialog.net cloud.ahch.datadialog.net pad.ahch.datadialog.net"
    echo -e "CUADDONSREPONAME is OPTIONAL! for the name of the custom-addons github repository! E.g.: cu_ahch"
    echo -e "                 Will use \"cu_{DATABASE_NAME}\" if not given!"
    echo -e "                 THIS PARAMETER IS OPTIONAL AND SHOULD NOT BE USED!"
    echo -e "ATTENTION: Make sure the github repository for the custom_addons already exists!"
    echo -e "ATTENTION: Make sure at least the default domains (see above) are already set up!"
    if [ $# -lt 5 ]; then
        echo -e "ERROR: \"setup-toosl.sh ${SCRIPT_MODE}\" needs a minimum of five arguments! \n       ${MODENEWDB}"
        exit 2
    fi

    # CONVENTIONS:
    # !!! Please read the TOOLS/README.md !!!

    # ----- Set Variables
    TARGET_BRANCH=$2
    SUPER_PASSWORD=$3
    DOMAIN_NAME=$5
    if $6; then
        CUADDONSREPONAME=$6
    else
        CUADDONSREPONAME="cu_$4"
    fi

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
    PUSHTODEPLOYPATH="${REPO_SETUPPATH}/node_modules/push-to-deploy"
    ETHERPADKEY=`tr -cd \#_[:alnum:] < /dev/urandom |  fold -w 16 | head -1`
    PUSHTODEPLOYSERVICENAME="${DBNAME}_${CUADDONSREPONAME}"
    PTDLOGFILE="${DBLOGPATH}/${DBNAME}-pushtodeply.log"
    GITPTDBRANCHNAME="${GITPATH}/${CUADDONSREPONAME}.git"

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
    useradd -m -d ${DBPATH} -s /bin/bash -U -G ${TARGET_BRANCH} -p $(echo "${LINUXPW}" | openssl passwd -1 -stdin) ${DBUSER} | tee -a ${INSTANCE_SETUPLOG}

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
    chown -R ${DBUSER}:${DBUSER} ${DBPATH} >> ${DB_SETUPLOG}
    chmod 755 ${DBPATH} >> ${DB_SETUPLOG}
    chown -R ${DBUSER}:${DBUSER} ${DBLOGPATH} >> ${DB_SETUPLOG}
    chmod 777 ${DBLOGPATH} >> ${DB_SETUPLOG}

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
    echo -e "\$1 Script Mode                    :  $SCRIPT_MODE" | tee -a ${DB_SETUPLOG}
    echo -e "\$2 TARGET_BRANCH                  :  $TARGET_BRANCH" | tee -a ${DB_SETUPLOG}
    echo -e "\$3 SUPER_PASSWORD                 :  $SUPER_PASSWORD" | tee -a ${DB_SETUPLOG}
    echo -e "\$4 DATABASE_NAME                  :  $4" | tee -a ${DB_SETUPLOG}
    echo -e "\$5 DOMAIN_NAME                    :  $DOMAIN_NAME" | tee -a ${DB_SETUPLOG}
    echo -e "\$6 CUADDONSREPONAME               : $CUADDONSREPONAME" | tee -a ${DB_SETUPLOG}
    echo -e ""
    echo -e "Database Setup Log File           :  ${DB_SETUPLOG}" | tee -a ${DB_SETUPLOG}
    echo -e ""
    echo -e "Database FINAL Name               :  $DBNAME" | tee -a ${DB_SETUPLOG}
    echo -e "Database Directory                :  $DBPATH" | tee -a ${DB_SETUPLOG}
    echo -e "Database Logfile                  :  $DBLOGFILE" | tee -a ${DB_SETUPLOG}
    echo -e "Database Baseport                 :  $BASEPORT" | tee -a ${DB_SETUPLOG}
    echo -e "Database Database User Name       :  $DBUSER" | tee -a ${DB_SETUPLOG}
    echo -e "Database Database User Password   :  $DBPW" | tee -a ${DB_SETUPLOG}
    echo -e "Database LINUX User               :  $DBUSER" | tee -a ${DB_SETUPLOG}
    echo -e "Database LINUX User Password      :  $LINUXPW" | tee -a ${DB_SETUPLOG}
    echo -e "Database Etherpad SESSION KEY     :  $ETHERPADKEY" | tee -a ${DB_SETUPLOG}
    echo -e "PUSHTODEPLOY Baseport             :  $BASEPORT" | tee -a ${DB_SETUPLOG}
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
        'psql -a -e -c "CREATE ROLE '${DBUSER}' WITH NOSUPERUSER CREATEDB LOGIN PASSWORD '\'${DBPW}\''"' | tee -a ${DB_SETUPLOG}

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
        }' ${INSTANCE_PATH}/TOOLS/server.conf > ${DBCONF} | tee -a ${DB_SETUPLOG}
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
        }' ${INSTANCE_PATH}/TOOLS/server.init > ${DBINIT} | tee -a ${DB_SETUPLOG}
    chown root:root ${DBINIT}
    chmod ugo=rx ${DBINIT}
    ln -s ${DBINIT} /etc/init.d/${DBNAME} | tee -a ${DB_SETUPLOG}
    update-rc.d ${DBNAME} start 20 2 3 5 . stop 80 0 1 4 6 . | tee -a ${DB_SETUPLOG}
    service ${DBNAME} start | tee -a ${DB_SETUPLOG}
    echo -e "Wait 8s for service ${DBNAME} to start..."
    sleep 8

    # ----- Create a new Database
    echo -e "\n----- Create Database ${DBNAME}"
    chmod 775 ${INSTANCE_PATH}/TOOLS/db-tools.py
    if ${INSTANCE_PATH}/TOOLS/db-tools.py -b ${BASEPORT}69 -s ${SUPER_PASSWORD} newdb -d ${DBNAME} -p adminpw ; then
        echo -e "Database created!" | tee -a ${DB_SETUPLOG}
    else
        echo -e "WARNING: Could not create Database ${DBNAME} !\nPlease create it manually!" | tee -a ${DB_SETUPLOG}
    fi

    # ----- Link Log Folder
    echo -e "\n---- Link ${DBLOGPATH} to ${DBPATH}/LOG"
    ln -s ${DBLOGPATH} ${DBPATH}/LOG | tee -a ${DB_SETUPLOG}

    # ----- Setup nginx
    echo -e "---- Create NGINX config file"
    touch ${PTDLOGFILE}
    chown ${DBNAME}: ${PTDLOGFILE}
    NGINXCONF=${DBPATH}/${DBNAME}-nginx.conf
    NGINXDBMAINTENANCEONLYFILE=${DBPATH}/${DBNAME}-maintenance
    /bin/sed '{
        s!BASEPORT!'"${BASEPORT}"'!g
        s!DBNAME!'"${DBNAME}"'!g
        s!DOMAIN_NAME!'"${DOMAIN_NAME}"'!g
        s!DBLOGPATH!'"${DBLOGPATH}"'!g
        s!DBPATH!'"${DBPATH}"'!g
        s!MAINTENANCEMODE!'"${NGINXDBMAINTENANCEONLYFILE}_ein"'!g
        s!PUSHTODEPLOYLOCATION!'"${CUADDONSREPONAME}"'!g
        s!PUSHTODEPLOYPORT!'"${BASEPORT}08"'!g
            }' ${INSTANCE_PATH}/TOOLS/nginx.conf > ${NGINXCONF} | tee -a ${DB_SETUPLOG}
    chown root:root ${NGINXCONF}
    chmod ugo=r ${NGINXCONF}
        touch ${NGINXDBMAINTENANCEONLYFILE}_aus
    ln -s ${NGINXCONF}  /etc/nginx/sites-enabled/${DBNAME}-${DOMAIN_NAME}
    service nginx restart
    echo -e "---- Create NGINX config file DONE"

    # ----- setup pushtodeploy and create - write init script and create config file
    echo "starting setup customer addons...."
    echo -e "---- Create pushtodeploy config file...."
    PUSHTODEPLOYCONF=${DBPATH}/${DBNAME}-pushtodeploy.yml
    /bin/sed '{
        s!PUSHTODEPLOYLOCATION!'"${CUADDONSREPONAME}"'!g
        s!INSTANZNAME!'"${DBNAME}"'!g
        s!DBPATH!'"${DBPATH}"'!g
            }' ${INSTANCE_PATH}/TOOLS/pushtodeploy.yml > ${PUSHTODEPLOYCONF} | tee -a ${DB_SETUPLOG}
    chown root:root ${PUSHTODEPLOYCONF}
    chmod ugo=r ${PUSHTODEPLOYCONF}
    echo -e "---- Create PUSHTODEPLOY config file DONE"
    echo -e "---- Create pushtodeploy init file..."
    PUSHTODEPLOYINIT=${DBPATH}/${DBNAME}-pushtodeploy.init
    /bin/sed '{
        s!'"DAEMON="'!'"DAEMON=${PUSHTODEPLOYPATH}/bin/push-to-deploy"'!g
        s!'"USER="'!'"USER=${DBUSER}"'!g
        s!'"PTDSERVICE"'!'"${PUSHTODEPLOYSERVICENAME}-${BASEPORT}08"'!g
        s!'"CONFIGFILE="'!'"CONFIGFILE=${PUSHTODEPLOYCONF}"'!g
        s!'"DAEMON_OPTS="'!'"DAEMON_OPTS=\"-p ${BASEPORT}08 ${PUSHTODEPLOYCONF}\""'!g
        s!LOGFILE=!'"LOGFILE=${PTDLOGFILE}"'!g
            }' ${INSTANCE_PATH}/TOOLS/pushtodeploy.init > ${PUSHTODEPLOYINIT} | tee -a ${DB_SETUPLOG}
    chown root:root ${PUSHTODEPLOYINIT}
    chmod ugo=rx ${PUSHTODEPLOYINIT}
    echo -e "---- Create PUSHTODEPLOY INIT file DONE"
    ln -s ${PUSHTODEPLOYINIT} /etc/init.d/${PUSHTODEPLOYSERVICENAME}-${BASEPORT}08
    echo "write Startup scripts"
    update-rc.d ${PUSHTODEPLOYSERVICENAME}-${BASEPORT}08 start 20 2 3 5 . stop 80 0 1 4 6 . | tee -a ${DB_SETUPLOG}
    echo "starting up push to deploy service"
    service ${PUSHTODEPLOYSERVICENAME}-${BASEPORT}08 start
    #/etc/init.d/${PUSHTODEPLOYSERVICENAME}-${BASEPORT}08
    echo "check if customer remote repository already exists"
    git ls-remote ${GITPTDBRANCHNAME} HEAD #if this command gets an exit code, it will be written into $? and can be checked
    if (( $? )); then
        echo "WARNING: ${GITPTDBRANCHNAME} does not exists, please create a new repo for this customer and create the webhook for this repo ${GITPTDBRANCHNAME}!"
        echo "and do manual -- git clone -b master ${GITPTDBRANCHNAME} ${DBPATH}/addons "
    else
        echo -e "repository ${GITPTDBRANCHNAME} exists .... Cloning Customer addons..."
        git clone -b master ${GITPTDBRANCHNAME} ${DBPATH}/addons | tee -a ${INSTANCE_SETUPLOG}
    fi
    chown -Rf ${DBUSER}:${DBUSER} ${DBPATH}/addons/ | tee -a ${DB_SETUPLOG}
    echo "finished setup pushtodeploy and create - write init script and create config file DONE"


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
    git clone -b master https://github.com/ether/etherpad-lite.git ${PADPATH} | tee -a ${DB_SETUPLOG}
    chown -R ${DBUSER}:${DBUSER} ${PADPATH} | tee -a ${DB_SETUPLOG}
    echo -e "\n---- Create etherpad-lite db role $PADUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${PADUSER}' WITH NOSUPERUSER LOGIN PASSWORD '\'${PADPW}\''"' | tee -a ${DB_SETUPLOG}
    # Create the owncloud database (utf8)
    # Create the etherpad database (utf8)
    echo -e "Create DB for etherpad-lite: ${PADDB} Owner: ${PADUSER}"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE DATABASE '${PADDB}' WITH OWNER '${PADUSER}' ENCODING '\'UTF8\''" ' | tee -a ${DB_SETUPLOG}
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
        }' ${INSTANCE_PATH}/TOOLS/etherpad.conf > ${PADCONF} | tee -a ${DB_SETUPLOG}
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
        }' ${INSTANCE_PATH}/TOOLS/etherpad.init > ${PADINIT} | tee -a ${DB_SETUPLOG}
    chown root:root ${PADINIT}
    chmod ugo=rx ${PADINIT}
    ln -s ${PADINIT} /etc/init.d/${DBNAME}-pad | tee -a ${DB_SETUPLOG}
    update-rc.d ${DBNAME}-pad start 20 2 3 5 . stop 80 0 1 4 6 . | tee -a ${DB_SETUPLOG}
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
    mkdir ${OWNCLOUDPATH}/data | tee -a ${DB_SETUPLOG}
    chown -R ${DBUSER}:${DBUSER} ${OWNCLOUDPATH} | tee -a ${DB_SETUPLOG}
    chown -R www-data:www-data ${OWNCLOUDPATH}/config/ ${OWNCLOUDPATH}/apps/ ${OWNCLOUDPATH}/data/ | tee -a ${DB_SETUPLOG}
    # Create owncloud db user
    echo -e "\n---- Create owncloud db role: $CLOUDUSER"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE ROLE '${CLOUDUSER}' WITH NOSUPERUSER LOGIN PASSWORD '\'${CLOUDPW}\''"' | tee -a ${DB_SETUPLOG}
    # Create the owncloud database (utf8)
    echo -e "\n---- Create owncloud DB: ${CLOUDDB}"
    echo -e "Create DB for owncloud: ${CLOUDDB} Owner: ${CLOUDUSER}"
    sudo su - postgres -c \
        'psql -a -e -c "CREATE DATABASE '${CLOUDDB}' WITH OWNER '${CLOUDUSER}' ENCODING '\'UTF8\''" ' | tee -a ${DB_SETUPLOG}
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
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${DBBACKUPSCRIPT} | tee -a ${DB_SETUPLOG}
    chown root:root ${DBBACKUPSCRIPT}
    chmod ugo=rx ${DBBACKUPSCRIPT}
    ln -s ${DBBACKUPSCRIPT} /etc/cron.daily/${DBNAME}-backup | tee -a ${DB_SETUPLOG}

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
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${PADDBBACKUPSCRIPT} | tee -a ${DB_SETUPLOG}
    chown root:root ${PADDBBACKUPSCRIPT}
    chmod ugo=rx ${PADDBBACKUPSCRIPT}
    ln -s ${PADDBBACKUPSCRIPT} /etc/cron.daily/${PADDB}-backup-pad | tee -a ${DB_SETUPLOG}

    # ----- Create backup script for OWNCLOUD and Setup cron job for backup script
    CLOUDDBBACKUPSCRIPT="${DBPATH}/${CLOUDDB}-backup-owncloud.sh"
    echo -e "Create PAD database backup script and link to cron daily"
    /bin/sed '{
        s!BASEPORT!'"$BASEPORT"'!g
        s!SUPER_PASSWORD!'"$SUPER_PASSWORD"'!g
        s!INSTANCE_PATH!'"$INSTANCE_PATH"'!g
        s!DBNAME!'"${CLOUDDB}"'!g
        s!DBBACKUPPATH!'"$DBBACKUPPATH"'!g
        s!BACKUPFILE!'"$DBBACKUPPATH/${CLOUDDB}"'!g
        s!BACKUPTYPE!'"owncloud-backup-sql"'!g
        s!DBPATH!'"${DBPATH}"'!g
        }' ${INSTANCE_PATH}/TOOLS/backup.sh > ${CLOUDDBBACKUPSCRIPT} | tee -a ${DB_SETUPLOG}
    chown root:root ${CLOUDDBBACKUPSCRIPT}
    chmod ugo=rx ${CLOUDDBBACKUPSCRIPT}
    ln -s ${CLOUDDBBACKUPSCRIPT} /etc/cron.daily/${CLOUDDB}-backup-owncloud | tee -a ${DB_SETUPLOG}

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
# $ odoo-tools.sh updateinst  {TARGET_BRANCH}
# ---------------------------------------------------------------------------------------
MODEUPDATEINST="$ odoo-tools.sh update  {TARGET_BRANCH}"
if [ "$SCRIPT_MODE" = "update" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATEINST"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 2 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly two arguments!"
        exit 2
    fi

    # TODO: Stop all o8_INSTANCENAME_* Services (remember all that where running!!!)
    # TODO: Stop all o8_INSTANCENAME PAD SERVICES (because etherpad-lite is maybe updated as well)
    # ATTENTION: Do not stop aeroo service (important if more than one instance is on the server)
    # Todo: git fetch, git checkout master, git pull, git checkout INSTANCENAME, git rebase
    # todo: start all pad services
    # todo: start the odoo services (only those who where running before)

    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MODEUPDATEINST DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
fi

MAINTENANCEMODE="$ odoo-tools.sh maintenancemode {TARGET_BRANCH} dbname|all enable|disable"
if [ "$SCRIPT_MODE" = "maintenancemode" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $MAINTENANCEMODE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 4 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly two arguments!"
        exit 2
    fi
    TARGET_BRANCH=$2
    DBNAME=$3
    OPTION=$4
    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"
    echo "Instanzpfad ${INSTANCE_PATH}"
    COUNTERFILE=${REPO_SETUPPATH}/${REPONAME}.counter
    GLOBALMAINTENANCELOG="${REPO_SETUPPATH}/${SCRIPT_MODE}--.log"
    DBMAINTENANCELOG="${INSTANCE_PATH}/${DBNAME}/$SCRIPT_MODE--${DBNAME}--.log"
    MAINTENANCEMODESWITCHERON="/usr/share/nginx/html/maintenance_ein"
    MAINTENANCEMODESWITCHEROFF="/usr/share/nginx/html/maintenance_aus"
    DBONLYMAINTENANCEMODESWITCHERON="${INSTANCE_PATH}/${DBNAME}/${DBNAME}-maintenance_ein"
    DBONLYMAINTENANCEMODESWITCHEROFF="${INSTANCE_PATH}/${DBNAME}/${DBNAME}-maintenance_aus"
    if [ ${OPTION} = "enable" ] || [ ${OPTION} = "disable" ]; then
        echo "starting maintenancemode check..."
    else
        echo -e "ERROR: check your enable disable parameter"
        exit 2
    fi
    # Check if a database with this name already exists (and exit with error if yes)
    if [ `su - postgres -c "psql -l | grep ${DBNAME} | wc -l"` -gt 0 ]; then
        echo -e "Database ${DBNAME} exists, starting maintenance mode checks"
    elif [ ${DBNAME} = "all" ]; then
        echo -e "All Nginx Instances will be switched into Maintenance mode"
    else
        echo -e "check your Databasename, you gave ${DBNAME}, but this seems not to exist, stopping script......"
        exit 2
    fi
    if ! [ -f ${COUNTERFILE} ]; then #no instance installed use different log dir
        if [ -f ${GLOBALMAINTENANCELOG} ]; then
            INSTANCE_RUNNING=0
        else
            touch ${GLOBALMAINTENANCELOG}
            INSTANCE_RUNNING=0
        fi
    else
        if [ -f ${DBMAINTENANCELOG} ]; then
            INSTANCE_RUNNING=1
        else
            touch ${DBMAINTENANCELOG}
            INSTANCE_RUNNING=1
        fi
    fi
    if [ ${INSTANCE_RUNNING} -eq 1 ]; then
    echo -e "starting maintenance checks..."

            #set Nginx in maintenance mode --> just rename /usr/share/nginx/html/maintenance_aus --> /usr/share/nginx/html/maintenance_ein
            #a rule in nginx.conf will check if the maintenance file is set or not
            # enable Maintenance mode
            if [ ${DBNAME} = "all" ]; then
                    if [ -f "${MAINTENANCEMODESWITCHEROFF}" ]; then
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "enabling global maintenancemode of nginx..."
                            mv ${MAINTENANCEMODESWITCHEROFF} ${MAINTENANCEMODESWITCHERON} | tee -a ${GLOBALMAINTENANCELOG}  #check
                        elif [ ${OPTION} = "disable" ]; then
                           echo -e "already disabled nothing to do..."
                           exit 2
                        fi
                    elif [ -f "{$MAINTENANCEMODESWITCHERON}" ]; then
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "already enabled nothing to do..."
                            exit 2
                        elif [ ${OPTION} = "disable" ]; then
                           echo -e "disable global maintenancemode of nginx..."
                            mv ${MAINTENANCEMODESWITCHERON} ${MAINTENANCEMODESWITCHEROFF} | tee -a ${GLOBALMAINTENANCELOG}  #check
                        fi
                    else
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "touching maintenancemode file seems someone deleted this file....."
                            touch ${MAINTENANCEMODESWITCHERON} | tee -a ${GLOBALMAINTENANCELOG}  #if file exists error occures but status is now correct
                        elif [ ${OPTION} = "disable" ]; then
                            echo -e "touching maintenancemode file seems someone deleted this file....."
                            touch ${MAINTENANCEMODESWITCHEROFF} | tee -a ${GLOBALMAINTENANCELOG}  #if file exists error occures but status is now correct
                        fi
                    fi

            else
                if [ -e "${DBONLYMAINTENANCEMODESWITCHEROFF}" ]; then
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "enabling ${DBNAME} maintenancemode of nginx..."
                            mv ${DBONLYMAINTENANCEMODESWITCHEROFF} ${DBONLYMAINTENANCEMODESWITCHERON} | tee -a ${DBMAINTENANCELOG}  #check
                        elif [ ${OPTION} = "disable" ]; then
                           echo -e "already disabled nothing to do..."
                           exit 2
                        fi
                elif [ -f "${DBONLYMAINTENANCEMODESWITCHERON}" ]; then
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "already enabled nothing to do..."
                            exit 2
                        elif [ ${OPTION} = "disable" ]; then
                           echo -e "disable ${DBNAME} maintenancemode of nginx..."
                            mv ${DBONLYMAINTENANCEMODESWITCHERON} ${DBONLYMAINTENANCEMODESWITCHEROFF} | tee -a ${DBMAINTENANCELOG}  #check
                        fi
                else
                        if [ ${OPTION} = "enable" ]; then
                            echo -e "touching maintenancemode file seems someone deleted this file....."
                            touch ${DBONLYMAINTENANCEMODESWITCHERON} | tee -a ${DBMAINTENANCELOG}  #if file exists error occures but status is now correct
                        elif [ ${OPTION} = "disable" ]; then
                            echo -e "touching maintenancemode file seems someone deleted this file....."
                            touch ${DBONLYMAINTENANCEMODESWITCHEROFF} | tee -a ${DBMAINTENANCELOG} #if file exists error occures but status is now correct
                        fi
                fi
            fi
            #init 4 also stops
            echo -e "Stopping nginx...."
            service nginx stop
            #ONLY STOPPING NGINX NO INSTANCE OR ANYTHING ELSE init 4 | tee -a $UPDATELOGFILE # stop all running processes postgres, openerp, pads, clouds
            echo -e "waiting 10 sec for recheck if all instances of nginx are stopped..."
            sleep 10 #wait for processes to be shut down
            #its a good idea to restart nginx this time staled processes aso are cleared now ...
            if [ "$(pgrep nginx)" = "" ]; then
                service nginx start
            else
                echo -e "could not stop everything clean so killing all nginx processes still running .... "
                killall nginx
                echo -e "restart nginx ....."
                service nginx start
            fi
    else
        echo "nothing todo for maintenancemode script, no instance running" >> ${GLOBALMAINTENANCELOG}
    fi
    #setzt die jeweilige instanz von Nginx in den maintenance mode oder den ganzen server
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e "MAINTENANCEMODE DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    exit 0
fi

UPDATETRANSLATION="$ odoo-tools.sh updatetranslation {BRANCH} {TARGET_DBNAME} {LANGUAGE} {MODULNAME} {UPDATETYPE} {WEBSITETEMPLATEMODUL}"
if [ "$SCRIPT_MODE" = "updatetranslation" ]; then
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e " $UPDATETRANSLATION"
    echo -e "--------------------------------------------------------------------------------------------------------"
    if [ $# -ne 7 ]; then
        echo -e "ERROR: \"setup-toosl.sh $SCRIPT_MODE\" takes exactly seven arguments!"
        exit 2
    fi
    TARGET_BRANCH=$2
    DBNAME=$3
    LANG=$4
    MODULNAME=$5
    UPDATETYPE=$6
    WEBSITETEMPLATEMODUL=$7 # this tranlsation should be loaded as last to make sure all others are overwritten with this latest customer specific translations
    INSTANCE_PATH="${REPOPATH}/${TARGET_BRANCH}"
    echo "Instanzpfad ${INSTANCE_PATH}"
    DATABASECONFIGFILE=${INSTANCE_PATH}/${DBNAME}/${DBNAME}.conf
    if [ ${UPDATETYPE} = "addonsownloaded" ]; then
        LANGUPDATEWORKINGPATH=${INSTANCE_PATH}/addons-loaded
    elif [ ${UPDATETYPE} = "cuaddonsonly" ]; then
        LANGUPDATEWORKINGPATH=${INSTANCE_PATH}/${DBNAME}/addons
    else
        echo "!!! WRONG UPDATETYPE PARAMETER aboring, check your parameters again ......"
        exit 2
    fi
    echo "stopping ${DBNAME} ..."
    service ${DBNAME} stop
    if [ ${LANG} = "all" ]; then
        if [ ${MODULNAME} = "all" ]; then
            echo "update all languages available in all customer modules"
            FILES=$(find ${LANGUPDATEWORKINGPATH} -name *.po)
            echo ${FILES}
            for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
            do
                echo "Processing $f file..."
                sudo su - ${DBNAME} -c \
                " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
            done
        else
            echo "update all languages available in ${MODULNAME} only"
            FILES=$(find ${LANGUPDATEWORKINGPATH}/${MODULNAME} -name *.po)
            echo ${FILES}
            for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
            do
                echo "Processing $f file..."
                sudo su - ${DBNAME} -c \
                 " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
            done
        fi
    else
        SINGLELANGUAGE=${LANG%_*} #get only first part of Language before underline
        echo "this is the single language: ${SINGLELANGUAGE}"
        if [ ${MODULNAME} = "all" ]; then
            echo "Updateing only ${LANG} in all customer modules"
            FILES=$(find ${LANGUPDATEWORKINGPATH} -name ${SINGLELANGUAGE}.po)
            echo ${FILES}
            for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
            do
                echo "Processing $f file..."
                sudo su - ${DBNAME} -c \
                " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
            done
        else
            echo "update only ${LANG} in ${MODULNAME} only"
            FILES=$(find ${LANGUPDATEWORKINGPATH}/${MODULNAME} -name ${SINGLELANGUAGE}.po)
            echo ${FILES}
            for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
            do
                echo "Processing $f file..."
                sudo su ${DBNAME} -c \
                " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
            done
    fi
    if ! [ ${WEBSITETEMPLATEMODUL} = "none" ]; then # make sure that the customers websitetemplate addon modul is loaded latest with all its specific translations
        if [ ${LANG} = "all" ]; then
            echo "update all languages available in all customer modules"
            if ! [ -n FILES=$(find ${INSTANCE_PATH}/${DBNAME}/addons/${WEBSITETEMPLATEMODUL} -name *.po) ]; then
                echo "module ${WEBSITETEMPLATEMODUL} not found check your parameters...."
                echo "Service will not start automatically"
                exit 2
            fi
            echo ${FILES}
            for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
            do
                echo "Processing $f file..."
                sudo su - ${DBNAME} -c \
                " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
            done
        else
            SINGLELANGUAGE=${LANG%_*} #get only first part of Language before underline
            echo "this is the single language: ${SINGLELANGUAGE}"
            if ! [ -n FILES=$(find ${INSTANCE_PATH}/${DBNAME}/addons/${WEBSITETEMPLATEMODUL} -name ${SINGLELANGUAGE}.po) ]; then
                echo "module ${WEBSITETEMPLATEMODUL} not found or no language files in there check your parameters...."
                echo "Service will not start automatically"
                exit 2
            fi
            echo "Updateing only ${LANG} in customer WEBSITEADDON MODULE"
                echo ${FILES}
                for f in ${FILES} #cycle all addons in addons-loaded and check langfile and path
                do
                    echo "Processing $f file..."
                    sudo su - ${DBNAME} -c \
                    " ${INSTANCE_PATH}/odoo/openerp-server -c ${DATABASECONFIGFILE} -d ${DBNAME} -l $LANG --i18n-import=${f} --i18n-overwrite"
                done
        fi
    else
        echo "no customer specific updates done....."
    fi
    echo "Starting up Database again...."
    service ${DBNAME} start
    echo -e "\n--------------------------------------------------------------------------------------------------------"
    echo -e "UPDATETRANSLATION DONE"
    echo -e "--------------------------------------------------------------------------------------------------------"
    exit 0
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
echo -e "TODO: $MODEDUPDB"
echo -e "TODO: $MODEUPDATEINST"
echo -e "$ $MAINTENANCEMODE"
echo -e "$ odoo-tools.sh updatetranslation {BRANCH} {TARGET_DBNAME} {LANGUAGE,de_DE|all} {MODULNAME,modulname|all} {UPDATETYPE,addonsownloaded|cuaddonsonly} {WEBSITETEMPLATEMODUL,website_pfot|none}"
echo -e "$ $MAINTENANCEMODE"
echo -e "TODO: $ odoo-tools.sh deployaddon {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "TODO: $MODEBACKUP"
echo -e "TODO: $MODERESTORE"
echo -e "------------------------\n"
