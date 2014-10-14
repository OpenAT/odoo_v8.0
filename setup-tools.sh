#!/bin/sh
# With the odoo setup tools you could

# Prepare ubuntu 14.01 LTS Server to work with odoo (postgres, nginx, python, pip-requirements)
# ./setup-tools.sh prepare

# Setup a new instance of oddo and configure nginx
# ./setup-tools.sh setup {customer-unique-shortcut} {external-web-url} {admin-password}

# Deploy / update an addon for some or all databases (restart service with -u)
# ./setup-tools.sh deploy {addonname} {dbnames or "all"}

# Backup some or all databases (and data-dir files in the zip)
# ./setup-tools.sh backup {dbnames seperated with , or "all"}

# Restore some or all databases (and data-dir files in the zip)
# ./setup-tools.sh restore {dbnames seperated with , or "all"}