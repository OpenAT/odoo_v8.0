# odoo_v8.0 Code Base
This repository is used as a codebase for odoo v8.0 and the related setup tools (odoo-tools.sh). 
The *master* branch of this repo is always a deploy-able production ready branch. 

## CONVENTIONS

### Branches:
The default latest stable branch is called master.
The other branches in the github repository are either production branches starting with "int" or "ext" (intdadi,
intdadirle, exthof) or development branches (setuptools, fix1234) that will be merged back into the master branch.

### Branch Names
- **freename** e.g.: *setuptools*  = Local Development branches that will be merged into master (deleted after merge)
- **fix[ISSUE Number]** e.g.: *fix1234*  = Developments related to Github Issues (deleted after merge)
- **int[customer id]** e.g.: *intdemo* = Production Instances hosted on our servers (our servers - also our hosted ones e.g.: at abaton)
- **ext[customer id]** e.g.: *exthof* = Production Instances hosted on customer servers (no control/payment for this servers from our side)

#### Examples of Branch Names on github:
- master (default stable branch)
- intdadi
- intdadirl1
- intdevel
- exthofe
- fix1234 (deleted after merge)
- setuptools (deleted after merge)

### Branch Updates (Deployment) for the odoo codebase:
The flow of fast-forward-branch-updates is always: master -> intdadi -> intdadirl1 - intdadirl2
Ext branches are normally not included in the update cycle.
Therefore and to make FF possible **merges or commits are never done directly in any "int" or "ext" branches**
Where int marks a server we pay (our own server) for and ext marks a server the custommer pays for (custommer server).


## GOALS

#### One Codebase (github repository) for all instances
- The branch determines the release (master=latest -> intdadi -> intdadirl1)
- All third party addons as well as odoo itself are linked as submodules and therefore tied with a specific commit

#### Simple setup and maintenance through odoo-tools.sh
**odoo-tools.sh** is a simple setup script that is able to
- **prepare** an ubuntu 14.04 LTS server to run odoo v8 (libs, tools, settings)
- **setup**/download the odoo code base for odoo v8 from github
- **newdb** create a new odoo instance:
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


## SETUP
This setup process will only work on a fresh install of Ubuntu 14.04 LTS. Make sure timezone is correct and the server
has internet access!


### 1.) Be Root ;)
```bash
ssh yourname@yourserver
sudo su
```

### 2.) get odoo-tools.sh
```bash
wget -O - https://raw.githubusercontent.com/OpenAT/odoo_v8.0/master/TOOLS/odoo-tools.sh > odoo-tools.sh
chmod 755 odoo-tools.sh
```

### 3.) Prepare the Ubuntu Server
```bash
odoo-tools.sh prepare
```
**Reboot the server!**

### 4.) Setup the odoo_v8.0 codebase (=branch):
```bash
# USAGE: odoo-tools.sh setup {TARGET_BRANCH}
odoo-tools.sh setup intdadi
```
This will create a new folder in **/opt/odoo_v8.0** called **intdadi**.

**HINT:** You can run **multiple branches on the same server!** All the branches will use and increment the same 
counter-file for the Database-Port therefore no port collisions can happen between Instances of different branches! 
A maximum of 99 Instances are possible for all installed branches!

### 5.) Create a new Instance:
**5.1) Create a new Github-Repository** manually for the custom-addons-folder of the new instance:
-  **Create a new Github-Repository** hosting the custom-addons of the instance:
    -  Where: https://github.com/OpenAT/
    -  Name: **cu_{DATABASE_NAME}* e.g.: cu_dadi (DATABASE_NAME should be the customer number e.g.: ahch or dadi)
- **Create a webhook** in the repository settings (https://github.com/OpenAT/cu_ahch/settings/hooks)
    - Payload Url: e.g.: ahch.datadialog.net/cu_ahch
    - Content Type: application/x-www-from-urlencoded

**5.2) Create the Default DNS-Entries for the new instance:**
- dadi.datadialog.net, \*.dadi.datadialog.net

**5.3) Install the new Instance:**
```bash
# usage: odoo-tools.sh newdb {TARGET_BRANCH} {SUPER_PASSWORD} {DATABASE_NAME} {DOMAIN_NAME} [CUADDONSREPONAME]
odoo-tools.sh newdb intdadi admin dadi www.datadialog.net
```
- Test/open the new instance
- Install addon base_config

**5.4) Save the installation summary in keepass!!!**

**5.5) Add the instance to the monitoring service**

**5.6) Ask the customer to set the correct DNS entries:**
www.datadialog.net, aswidget.www.datadialog.net, pad.www.datadialog.net, cloud.www.datadialog.net


## DEVELOPMENT

To develop with this repo use this workflow:

```bash
# 1.) Clone the repo odoo_v8 branch master locally:
git clone -b master --recurse-submodules https://github.com/OpenAT/odoo_v8.0.git ${instance_dir}

# Check if the upstream (remote) is set correctly for the master branch
git branch -vv
git --set-upstream-to=https://github.com/OpenAT/odoo_v8.0.git master    # creates remotes and origin

# 2.) Create and checkout a new branch:
git branch dev-ckeditor_advanced
git checkout dev-ckeditor_advanced

# 3.) Push your Branch to Github (so everybody knows what you are working on)
git commit
git push origin dev-ckeditor_advanced

# 4.) Do stuff and commit and push changes until ready:
git add [file or folders]    # This tells git what to include in next commit
git commit -m "[ADD] Added README.md"
git push origin dev-ckeditor_advanced

# 5.) When ready with development 
# - create pull request on github (at webpage) if wanted to discuss / review changes
# - Update master branch to latest
# - rebase dev-ckeditor_advanced on master
# - rebase dev-ckeditor_advanced submodules on master
# - merge dev-ckeditor_advanced in master with rebase
git fetch
git checkout master    # NOW IN BRANCH master
git pull
git checkout dev-ckeditor_advanced    # NOW IN BRANCH dev-ckeditor_advanced
git rebase master
git submodule update
git checkout master    # NOW IN BRANCH master
git merge dev-ckeditor_advanced
git push origin master
```

Adding new Submodules to the repo:
```bash
# This is an example how to add a submodule:
git submodule add -b master https://github.com/ether/etherpad-lite.git etherpad-lite

# Ubdate all submodules
git submodule update --rebase --remote --recursive
```


## UPDATE OF AN INSTANCE (and its DBs)

This is for now only a placeholder but will describe the update process of a customer instance.
```bash

# Update Master
git checkout master                             
git pull                                        
git submodule update

# Update Branch (Code Repo for a server in this case)
git checkout intdadi                            
git rebase master
git submodule update
git push origin intdadi
```


## Update of all Submodules of branch master
```bash
git checkout master
git pull
git submodule update --remote --rebase --recursive
git commit -am "[UPDATE] all submodules updated"
git push master
```

## DOCUMENTATION

#### odoo v8
- [Latest Dev Docu](https://www.odoo.com/documentation/master/howtos/website.html)
- [odoo v8 api guidelines](http://odoo-new-api-guide-line.readthedocs.org/en/latest/)
- [Technical Memento](https://www.odoo.com/files/memento/OpenERP_Technical_Memento_latest.pdf)
- [eval many2many write](https://doc.odoo.com/v6.0/developer/2_5_Objects_Fields_Methods/methods.html/#osv.osv.osv.write)
- [WebApps Tutorial HBEE](https://www.hbee.eu/en-us/blog/archive/2014/9/17/odoo-web-apps/)
- [Forum how to's](https://www.odoo.com/forum/how-to)

#### Configuration (res.config) related
- https://www.odoo.com/forum/help-1/question/how-can-i-save-load-my-own-configuration-settings-30123
- https://www.odoo.com/forum/help-1/question/how-can-i-create-own-config-for-my-custom-module-41981
- https://www.odoo.com/forum/help-1/question/is-it-possible-to-set-database-default-configuration-values-507
- https://doc.odoo.com/6.0/developer/5_16_data_serialization/xml_serialization/
- http://stackoverflow.com/questions/9377402/insert-into-many-to-many-openerp/9387447#9387447

#### Other odoo Tools and Docs
- [carddav for odoo](https://github.com/initOS/openerp-dav)
- http://odoohub.wordpress.com/2014/08/15/where-is-the-odoo-documentation/
- http://djpatelblog.blogspot.in/2014/09/odoo-new-api-recordsets.html
- [server.conf db_filter= parameter](https://www.odoo.com/forum/help-1/question/domain-based-db-filter-6583)

#### XMLRPC, ErpPeek, Connector ...
- [XMLRPC and erppeek by wirtel](http://wirtel.be/posts/en/2014/06/13/using_erppeek_to_discuss_with_openerp/)
- [erppeek](http://erppeek.readthedocs.org/en/latest/index.html)
- [oerplib](https://github.com/osiell/oerplib)
- [oerlib docu](https://pythonhosted.org/OERPLib/#supported-openerp-odoo-server-versions)
- [xmlrpc lib docu](https://docs.python.org/2/library/xmlrpclib.html)
- [odoo connector](http://odoo-connector.com)

#### git, git workflow and github
- [Github Rebase Workflow](http://mettadore.com/2011/09/07/the-ever-deployable-github-workflow/)
- [Git Submodules](http://git-scm.com/docs/git-submodule)
- [Github Using Pull Requests](https://help.github.com/articles/using-pull-requests/)
- [Adding an existing project to github](https://help.github.com/articles/adding-an-existing-project-to-github-using-the-command-line/)
- [Push to a Remote](https://help.github.com/articles/pushing-to-a-remote/)
- [README.md Markdown Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

#### Odoo Setup in Ubuntu 14.04 LTS
- [nginx and odoo](http://wirtel.be/posts/en/2011/11/02/nginx-proxy-openerp/)
- [odoo v7 setup scripts](https://github.com/OpenAT/odoo-tools/tree/7.0)
- [odoo 8 setup script by Andre Schenkel](https://github.com/lukebranch/odoo-install-scripts/blob/master/odoo-saas4/ubuntu-14-04/odoo_install.sh)
- [odoo setup ubuntu 14 lts](https://www.odoo.com/forum/help-1/question/how-to-install-odoo-from-github-on-ubuntu-14-04-for-testing-purposes-only-ie-not-for-production-52627)

#### Python, PIP, VirtualEnv
- [PYTHON](https://www.python.org)
- [Python Quick Ref](http://rgruet.free.fr/#QuickRef)
- [PIP Docu](http://pip.readthedocs.org/en/latest/user_guide.html#requirements-files)
- [argparse](https://docs.python.org/2.7/library/argparse.html#other-utilities)

#### BASH Scripting
- [if conditions](http://www.tldp.org/LDP/Bash-Beginners-Guide/html/sect_07_01.html)
- [sed](http://wiki.ubuntuusers.de/sed)

#### Java Script
- https://developer.mozilla.org/de/docs/Web/JavaScript
