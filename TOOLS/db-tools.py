#!/usr/bin/env python
# We are talking to the running odoo server through xmlrpc
#
# look at "odoo/openerp/service/db.py" or common.py or modules.py and search for "def dispatch(...)" : there you can
# find all the available xmlrpc methods
#
# ATTENTION: be aware that for most db.py methods the fist argument is always the SUPER_PASSWORD
#            look at: passwd = params[0] and params = params[1:]
import sys
import argparse
import base64
from xmlrpclib import ServerProxy


# Create database
def newdb(args):
    # Create the Database
    # service/db.py:   def exp_create_database(db_name, demo, lang, user_password='admin'):
    print 'Creating Database: %s' % args.database
    if server.create_database(args.superpwd, args.database, False, 'de_DE', args.password):
        sys.exit(0)
    else:
        sys.exit(2)
        
# Duplicate Database:
def dupdb(args):
    # Duplicate the Database
    # service/db.py:   def exp_duplicate_database(db_original_name, db_name):
    print 'Duplicate Database: %s' % args.database
    if server.duplicate_database(args.superpwd, args.database, args.template):
        sys.exit(0)
    else:
        sys.exit(2)

# Backup DB
# service/db.py:   def exp_dump(db_name):
def backup(args):
    with open(args.filedump, 'w') as f:
        f.write(server.dump(args.superpwd, args.database).decode('base64'))
        if f:
            print 'Database Backup File Name: %s' % f.name
            sys.exit(0)
        else:
            sys.exit(2)

# Restore DB
# service/db.py:   def exp_restore(db_name, data, copy=False):
def restore(args):
    print 'Restore Database: %s' % args.database
    with open(args.filedump) as dump_file:
        if server.restore(args.superpwd, args.database, base64.b64encode(dump_file.read())):
            sys.exit(0)
        else:
            sys.exit(2)

# DROP DB
# service/db.py:   def exp_drop(db_name):
def drop(args):
    print 'Drop Database: %s' % args.database
    if server.drop(args.superpwd, args.database):
        sys.exit(0)
    else:
        sys.exit(2)

# ----------------------------
# Create the command parser
# ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--baseport', required='True', help='XMLRPC Port')
parser.add_argument('-s', '--superpwd', required='True', help='Super Password')
subparsers = parser.add_subparsers(title='subcommands',
                                   description='available subcommands',
                                   help='')

# SubParser for newdb
parser_newdb = subparsers.add_parser('newdb', help='Create a new DB or duplicate existing if -t given.')
parser_newdb.add_argument('-d', '--database', required='True', help='Name of new database')
parser_newdb.add_argument('-p', '--password', required='True', help='Password for user "admin"')
parser_newdb.set_defaults(func=newdb)

# SubParser for dubdb
parser_dupdb = subparsers.add_parser('dupdb', help='Create a new DB or duplicate existing if -t given.')
parser_dupdb.add_argument('-d', '--database', required='True', help='Name of new database')
parser_dupdb.add_argument('-t', '--template', help='Existing database to duplicate')
parser_dupdb.set_defaults(func=dupdb)

# SubParser for backup
parser_backup = subparsers.add_parser('backup', help='Backup database with data-dir as zip file.')
parser_backup.add_argument('-d', '--database', required='True', help='Database to backup')
parser_backup.add_argument('-f', '--filedump', required='False', help='Backupfile')
parser_backup.set_defaults(func=backup)

# SubParser for restore
parser_restore = subparsers.add_parser('restore', help='restore database with data-dir as zip file.')
parser_restore.add_argument('-d', '--database', required='True', help='Name of new database')
parser_restore.add_argument('-f', '--filedump', required='True', help='Backupfile to restore')
parser_restore.set_defaults(func=restore)

# SubParser for restore
parser_drop = subparsers.add_parser('drop', help='drop database.')
parser_drop.add_argument('-d', '--database', required='True', help='Name of database')
parser_drop.set_defaults(func=restore)

# --------------------
# START
# --------------------
args = parser.parse_args()
print 'DEBUG: args: %s' % args

# XMLRPC Proxy Connection
server = ServerProxy('http://localhost:'+str(args.baseport)+'/xmlrpc/db')
print "server: %s" % server

# Call method argparse.ArgumentParser.parse_args.func() of object parser
args.func(args)
