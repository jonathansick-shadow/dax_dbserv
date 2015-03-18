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

from flask import Blueprint, request
import json

from lsst.db.dbPool import DbPool


dbREST = Blueprint('dbREST', __name__, template_folder='dbserv')

# Connect to the metaserv database. Note that the metaserv typically runs for
# a long time, and the connection can timeout if there long period of inactivity.
# Use the DbPool, which will keep the connection alive.
dbPool = DbPool()
dbPool.addConn("c1", read_default_file="~/.lsst/dbAuth-dbServ.txt")


def runDbQueryM(query, optParams=None):
    '''Runs query that returns many rows. Returns properly formatted result. It can
    raise DbException or mysql exception.'''
    rows = dbPool.getConn("c1").execCommandN(query, optParams)
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    retStr = ''
    if len(rows) > 0:
        if fmt == 'text/html':
            for row in rows:
                for c in row:
                    retStr += "%s " % c
                retStr += "<br><br>"
        else: # default format is application/json
            retStr = json.dumps(rows)
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
        sql = request.args.get('sql').encode('utf8')
        # TODO: query validation. See DM-2138
        return runDbQueryM(sql)
    else:
        return "Listing queries is not implemented."
