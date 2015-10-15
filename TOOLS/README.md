#Odoo Setup Tools
**odoo-tools.sh** is a simple setup script that is able to:

- **prepare** an ubuntu 14.04 LTS server to run odoo v8 (libs, tools, settings)
- **setup**/download the odoo code base for odoo v8 from github
- **newdb** = create a new odoo instance:
    - linux user
    - database creation
    - postgres user
    - server.conf und server.init
    - etherpad
    - owncloud
    - nginx setup (match urls to instance via vhosts) and setup default URLs e.g.: ahch.datadialog.net, aswidget.ahch.datadialog.net, cloud.ahch.datadialog.net, pad.ahch.datadialog.net
    - backup and logrotate cron jobs
    - create and link custom-addons githup repository into the instance addons folder
    - Install push-to-deploy workflow for updating the custom addons folder
- **duplicatedb** duplicate an instance (TODO!)
- **update** one or all instances to the latest master branch (TODO!)
    - clone the server (VMWare)
    - create new snapshot on the clone
    - backup instances on the clone
    - Try the update(s) on the clone (one by one) and if it all worked:
    - Do the Updates on the production machine
- **maintenancemode** set one or all instances into maintenance mode (not reachable from the outside)
- **backup** one or all instances
- **restore** one or all instances (TODO!)
- ToDo: deploy addon(s) to one or more databases on the local server

**HINT:** **db-tools.sh** is used by odoo-tools.sh to backup and restore the database and data-dir of an instance.

##CONVENTIONS:

###Github Repository:
The Github repository used for the odoo code base is "hardcoded" in the github repository they are in!
For odoo 8 we use the github repository https://github.com/OpenAT/odoo_v8.0.git

(If we start the development for odoo 9 we will copy the github repo from odoo_v8.0.git to odoo_v9.0.git and then we
need to change all related paths in the setup tools.)

###Branch
The Branch used for any instance must be installed first with "odoo-tools.sh setup {TARGET_BRANCH}"
This will create a new folder in **/opt/odoo_v8.0** called **{TARGET_BRANCH}** and serves as a codebase for instances.

**HINT:** You can run **multiple branches on the same server!** All the branches will use and increment the same 
counter-file for the Database-Port therefore no port collisions can happen between Instances of different branches! 
A maximum of 99 Instances are possible for all installed branches!

###Variable Names:
Use PATH in Variable Names that contain file paths! Use no trailing "/"
    RIGHT: TEST_PATH="${REPOPATH}/test"    WRONG: TEST="${REPOPATH}/test/"
Variable Names without "PATH" can contain anything including files with paths e.g. DB_SETUPLOG

###Port Schema:
```
[v][dd][pp]         [v]=Odoo_Version [dd]=Instance/Database  [pp]=Instance_Services

Odoo Versions [v] (0-9):
    4 = odoo OLD setups 6or7 old install
    1 = odoo v8.0
    2 = odoo v9.0

Instance (Database) Counter [dd] (00-99):
    This is the BASEPORT of the Instance

Usabel Ports per Instance [pp] (00-99):
    69 = odoo xmlrpc 
    08 = push to deploy

Example: the first instance on a new odoo_v8.0 Server:
[1][01][ports]
10169 = odoo xmlrpc port of instance 01
   71 = odoo xmlrpcs_port
   79 = odoo longpolling_port
   08 = push to deploy port
   91 = Etherpad Pad Server
```
Therefore **only 99 Instances are possible for all branches** installed on this server because
the same Database Counter File (BASEPORT) is used by every branch.

###Database Name:
**Must be the unique customer number** E.g.: pfot, ahch, dadi, ... (or something like tierdemo, shopdev, ...)

###Custom Addons Folder:
CUADDONSREPONAME = is the name of the customer github repository! E.g.: cu_ahch"
                   THIS PARAMETER IS OPTIONAL AND SHOULD NOT BE USED!
                   Will use \"cu_{DATABASE_NAME}\" if not given!