#!/bin/bash
#######################################################################################################################

SOURCE_BRANCH="odoo_v8.0"
SCRIPT_MODE=$1

# ---------------------------------------------------------
# SCRIPT START
# ---------------------------------------------------------
echo -e "\n----- SCRIPT START odoo-tools.sh -----"

# ----- Set Script Path:
# "/home/user/bin/foo.sh"
SCRIPT=$(readlink -f "$0")
# "/home/user/bin"
SCRIPTPATH=$(cd ${0%/*} && pwd -P)

# ----- Check UBUNTU Version:
source /etc/lsb-release
if [ $DISTRIB_ID = "Ubuntu" ] && [ $DISTRIB_RELEASE = "14.04" ] ; then
    echo "\nOS Version: $$DISTRIB_ID $DISTRIB_RELEASE"
else
    echo "\nERROR: This Script only works on Ubuntu 14.04!"
    exit 2
fi

# ----- Check script is started as root:
if [ "$EUID" -ne 0 ]; then
    echo "\nERROR: Please run as root!"
    exit 2
fi

# ----- Base Path for all odoo instances:
BASEPATH="/opt/odoo"
if cd $BASEPATH ; then
    echo -e "\nChanged directory to $BASEPATH"
else
    if mkdir $BASEPATH ; then
	    echo -e "\nCreated directory $BASEPATH"
	    cd $BASEPATH
	    echo -e "\nChanged directory to $BASEPATH"
    else
        echo -e "\nERROR: Could not create directory $BASEPATH!"
	    exit 2
    fi
fi

# ----- SETUP LOG-File:
SETUP_LOG="${BASEPATH}/oe-prepare_system.log"
if -w $SETUP_LOG ; then
    echo -e "\n Setup log file ist at ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
else
    if touch $SETUP_LOG ; then
        echo -e "\n Setup log file ist at ${SETUP_LOG}. DO NOT MODIFY OR DELETE!"
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
if [ $SCRIPT_MODE = "prepare" ]; then
    echo -e "\n----- odoo-tools.sh PREPARE -----\n"
    if [ $# -ne 1 ]; then
        echo -e "\nERROR: \"setup-toosl.sh prepare\" takes exactly one argument!"
        exit 2
    fi

    # ----- Update Server
    echo -e "\n----- Update Server"
    apt-get update >> $SETUP_LOG
    apt-get upgrade -y >> $SETUP_LOG
    echo -e "\n----- Update Server Done"

    # ----- Install Basic Packages
    echo -e "\n----- Install Basic Packages"
    apt-get install ssh wget sed git git-core gzip curl python libssl-dev build-essential -y >> $SETUP_LOG
    echo -e "\n----- Install Basic Packages Done"

    # ----- Install postgresql
    echo -e "\n----- Install postgresql"
    apt-get install postgresql postgresql-server-dev-9.3 libpq-dev >> $SETUP_LOG
    update-rc.d postgresql defaults >> $SETUP_LOG
    service postgresql restart | tee -a $SETUP_LOG
    echo -e "\n----- Install postgresql Done"

    # ----- Install nginx
    echo -e "\n----- Install nginx"
    apt-get remove apache2 apache2-mpm-event apache2-mpm-prefork apache2-mpm-worker -y >> $SETUP_LOG
    apt-get install nginx -y >> $SETUP_LOG
    update-rc.d nginx defaults >> $SETUP_LOG
    service nginx restart | tee -a $SETUP_LOG
    echo -e "\n----- Install nginx Done"

    # ----- Install Python Packages
    echo -e "\n----- Install Python Packages"
    apt-get install python-pip python-dev python-software-properties  -y >> $SETUP_LOG
    apt-get install libjpeg-dev libjpeg8-dev libtiff5-dev vflib3-dev pngtools libpng3 -y >> $SETUP_LOG
    apt-get install xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic -y >> $SETUP_LOG
    apt-get install wkhtmltopdf -y >> $SETUP_LOG
    apt-get install flashplugin-nonfree -y >> $SETUP_LOG
    pip install git+https://github.com/qoda/python-wkhtmltopdf.git >> $SETUP_LOG
    echo -e "\nInstall requirements.txt"
    wget -O- https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/requirements.txt > $BASEPATH/requirements.txt
    pip install -r $BASEPATH/requirements.txt | tee -a $SETUP_LOG
    echo -e "\n----- Install Python Packages Done"

    # ----- Install Packages for AerooReports
    echo -e "\n----- Install Packages for AerooReports"
    apt-get install python-genshi python-pyhyphen ure uno-libs3 unoconv libxml2-dev libxslt-dev \
                    libreoffice-core libreoffice-common libreoffice-base libreoffice-base-core \
                    libreoffice-draw libreoffice-calc libreoffice-writer libreoffice-impress \
                    python-cupshelpers hyphen-de hyphen-en-us -y >> $SETUP_LOG
    echo -e "\nInstall Aeroolib"
    git clone --depth 1 --single-branch https://github.com/aeroo/aeroolib.git $BASEPATH/aeroolib >> $SETUP_LOG
    python $BASEPATH/aeroolib/aeroolib/setup.py install | tee -a $SETUP_LOG
    echo -e "\nInstall Aeroo LibreOffice Service"
    wget -O- https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/aeroo.init > $BASEPATH/aeroo.init
    ln -s $BASEPATH/aeroo.init /etc/init.d/aeroo.init >> $SETUP_LOG
    update-rc.d aeroo defaults >> $SETUP_LOG
    service aeroo stop >> $SETUP_LOG
    service aeroo start | tee -a $SETUP_LOG
    echo -e "\n----- Install Packages for AerooReports Done"

    # ----- Install Packages for Etherpad Lite
    echo -e "\nInstall Packages for Etherpad Lite"
    apt-get install nodejs abiword -y >> $SETUP_LOG
    echo -e "\nInstall Packages for Etherpad Lite Done"


fi


# ---------------------------------------------------------
# Script HELP
# ---------------------------------------------------------
echo -e "\n\n----- SCRIPT USAGE -----"
echo -e "\n$ odoo-tools.sh {prepare|setup|deploy|backup|restore} ...\n"
echo -e "\n$ odoo-tools.sh prepare"
echo -e "\n$ odoo-tools.sh setup   {TARGET_BRANCH} {SUPER_PASSWORD} {DOMAIN_NAME}"
echo -e "\n$ odoo-tools.sh deploy  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all} {ADDON,ADDON}"
echo -e "\n$ odoo-tools.sh backup  {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME,DBNAME|all}"
echo -e "\n$ odoo-tools.sh restore {TARGET_BRANCH} {SUPER_PASSWORD} {DBNAME} {DUMP_TO_RESTORE}"
echo -e "\n------------------------\n"