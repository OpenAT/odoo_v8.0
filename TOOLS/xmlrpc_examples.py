#!/usr/bin/env python
# We are talking to the running odoo server through xmlrpc
#
# look at "odoo/openerp/service/db.py" or common.py or modules.py and search for "def dispatch(...)" : there you can
# find all the available xmlrpc methods
#
# ATTENTION: be aware that for most db.py methods the fist argument is always the SUPER_PASSWORD
#            look at: passwd = params[0] and params = params[1:]
import os
import sys
import argparse
import tempfile
from xmlrpclib import ServerProxy


# --------------------
# START
# --------------------
#args = parser.parse_args()
print 'DEBUG: args: %s' % args

# XMLRPC Proxy Connection
server = ServerProxy('http://localhost:'+str(args.baseport)+'/xmlrpc/db')
print "server: %s" % server

# Call method argparse.ArgumentParser.parse_args.func() of object parser
args.func(args)


server.execute_kw('test', 1, 'admin', 'res.partner', 'create', [{'name': 'hugo2', 'country_id': search([[['name', '=', 'Austria']]])}])
server.execute_kw('test', 1, 'admin', 'res.country', 'search', [[['code', '=', 'AG']]])

listepos1 = server.execute_kw('test', 1, 'admin', 'res.country', 'search', [[['code', '=', 'AG']]])


