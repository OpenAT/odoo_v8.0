#!/usr/bin/env python
# We are talking to the running odoo server through xmlrpc
#
# look at "odoo/openerp/service/db.py" or common.py or modules.py and search for "def dispatch(...)" : there you can
# find all the available xmlrpc methods
#
# ATTENTION: be aware that for most db.py methods the fist argument is always the SUPER_PASSWORD
#            look at: passwd = params[0] and params = params[1:]
import sys
import optparse

from xmlrpclib import ServerProxy

parser = optparse.OptionParser()
parser.add_option('-b', '--baseport', dest='baseport', help='XMLRPC Port')
parser.add_option('-s', '--superpw', dest='superpw', help='Super Password')
parser.add_option('-d', '--database', dest='dbname', help='Database Name')
parser.add_option('-p', '--password', dest='dbpw', help='Database Password')

(options, args) = parser.parse_args()


# XMLRPC Proxy Connection
server = ServerProxy('http://localhost:'+str(options.baseport)+'/xmlrpc/db')

# ---- Check if the Database already exists
if server.db_exist(options.dbname):
    print 'Databasename already used'
    sys.exit(2)

# ---- Create the Database
#server.create_database(super_password, db_name, demo, lang, user_password='admin')
print 'Creating Database'
server.create_database(options.superpw, options.dbname, 'False', 'de_DE', options.dbpw)
sys.exit(0)
