#!/usr/bin/env python

# LSST Data Management System
# Copyright 2015 AURA/LSST.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.

"""
This module implements the RESTful interface for Databaser Service.
Corresponding URI: /db. Default output format is json. Currently
supported formats: json and html.

@author  Jacek Becla, SLAC

# todos:
#  * migrate to db, and use execCommands etc from there.
#  * generate proper html header
"""

from flask import Blueprint, Flask, request
import json
import MySQLdb

from lsst.db.utils import readCredentialFile
import lsst.log as log


dbREST = Blueprint('dbREST', __name__, template_folder='dbserv')

# connect to the database
creds = readCredentialFile("~/.lsst/dbAuth-dbServ.txt", log)
try:
    con = MySQLdb.connect(host=creds['host'],
                          port=int(creds['port']),
                          user=creds['user'],
                          passwd=creds['passwd'])

except MySQLdb.Error as err:
    log.info("ERROR MySQL %s", err)
    raise

def runDbQuery1(query, optTuple=None):
    '''Runs query that returns one row.'''
    cursor = con.cursor()
    if optTuple:
        cursor.execute(query, optTuple)
    else:
        cursor.execute(query)
    row = cursor.fetchone()
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    retStr = ''
    if row:
        for x in range(0, len(row)):
            if fmt == "text/html":
                retStr += "%s: %s<br />" % (cursor.description[x][0], row[x])
            else: # default format is application/json
                retStr += "%s:%s " % (cursor.description[x][0], row[x])
        if fmt == "application/json":
            retStr = json.dumps(retStr)
    cursor.close()
    return retStr

def runDbQueryM(query, optTuple=None):
    '''Runs query that returns many rows.'''
    cursor = con.cursor()
    if optTuple:
        cursor.execute(query, optTuple)
    else:
        cursor.execute(query)
    rows = cursor.fetchall()
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    retStr = ''
    if len(rows) > 0:
        if fmt == 'text/html':
            retStr = "<br />".join(str(r[0]) for r in rows)
        else: # default format is application/json
            ret = " ".join(str(r[0]) for r in rows)
            retStr = json.dumps(ret)
    cursor.close()
    return retStr

@dbREST.route('/', methods=['GET'])
def getRoot():
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if fmt == 'text/html':
        return ("LSST Database Service v0 here. I currently support: "
                "<a href='query'>/query</a>.")
    return "LSST Database Service v0 here. I currently support: /query."

@dbREST.route('/query', methods=['GET'])
def getQuery():
    '''If sql is not passed, it lists quries running for a given user.
       If sql is passed, it runs a given query.'''
    if 'sql' in request.args:
        sql = request.args.get('sql')
        # I'm sure we will want to do some validation here, etc, this is
        # a very first version
        return runDbQueryM(sql)
    else:
        return "Listing queries is not implemented."
