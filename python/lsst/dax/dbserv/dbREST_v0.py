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

from base64 import b64encode
from datetime import date, datetime, time, timedelta
from flask import Blueprint, request, current_app, make_response
from httplib import OK, INTERNAL_SERVER_ERROR
import json
import logging as log
from lsst.dax.webservcommon import renderJsonResponse
import MySQLdb
from MySQLdb.constants.FLAG import BINARY
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

dbREST = Blueprint('dbREST', __name__, template_folder='dax_dbserv')


@dbREST.route('/', methods=['GET'])
def getRoot():
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if fmt == 'text/html':
        return "LSST Database Service v0 here. I currently support: " \
               "<a href='query'>/query</a>."
    return "LSST Database Service v0 here. I currently support: /query."

_error = lambda exception, message: {"exception": exception, "message": message}
_vector = lambda results, metadata: {"results": results, "metadata": metadata}


@dbREST.route('/query', methods=['GET'])
def getQuery():
    '''If sql is not passed, it lists quries running for a given user.
       If sql is passed, it runs a given query.'''
    if 'sql' in request.args:
        sql = request.args.get('sql').encode('utf8')
        log.debug(sql)
        try:
            engine = current_app.config["default_engine"]
            results = []
            helpers = []
            rows = engine.execute(text(sql))
            curs = rows.cursor

            for result in rows:
                # If this is the first time, build column definitions (use raw values to help)
                if not helpers:
                    for desc, flags, val in zip(curs.description, curs.description_flags, result):
                        helpers.append(ColumnHelper(desc, flags, val))

                # Not streaming...
                results.append([helper.checkValue(val) for helper, val in zip(helpers, result)])

            status_code = OK
            metadata = {"columnDefs": [{"name": cd.name, "type": cd.type} for cd in helpers]}
            response = _vector(results, metadata)
        except SQLAlchemyError as e:
            log.debug("Encountered an error processing request: '%s'" % e.message)
            response = _error(type(e).__name__, e.message)
            status_code = INTERNAL_SERVER_ERROR
        return _response(response, status_code)
    else:
        return "Listing queries is not implemented."


def _response(response, status_code):
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if fmt == 'text/html':
        response = renderJsonResponse(response=response, status_code=status_code)
    else:
        response = json.dumps(response)
    return make_response(response, status_code)


class ColumnHelper:

    def __init__(self, description, flags, value):
        """
        Helper class to define a column, get it's type for conversion, and convert types if needed.
        This class works on a best-effort basis. It's not guaranteed to be 100% correct.
        @param name: Column name
        @param flags: Flags from MySQLdb.constants.FLAGS
        @param value: An example value type to help with inferring how to convert
        """
        self.type = None
        self.converter = None
        self.name = description[0]

        type_code = description[1]
        scale = description[5]

        if type_code in MySQLdb.NUMBER:
            # Use python types first, fallback on float otherwise (e.g. NoneType)
            if isinstance(value, int):
                self.type = "int"
            else:
                # If there's a scale, use float, otherwise assume long
                self.type = "float" if scale else "long"

        # Check datetime and date
        if type_code in MySQLdb.DATETIME:
            self.type = "timestamp"
            self.converter = lambda x: x.isoformat()
        if type_code in MySQLdb.DATE:
            self.type = "date"
            self.converter = lambda x: x.isoformat()

        # Check if this is binary data and potentially unsafe for JSON
        if not self.type and flags & BINARY and type_code not in MySQLdb.TIME:
            # This needs to be checked BEFORE the next type check
            self.type = "binary"
            self.converter = b64encode
        elif isinstance(value, str):
            self.type = "string"

        if not self.type:
            # Just return a string and make sure to convert it to string if we don't know about
            # this type. This may include datetime.time
            self.type = "string"
            self.converter = str

    def checkValue(self, value):
        """
        Check the value returned from the DBAPI.
        @param value:
        @return: The value itself, or a stringified version if it needs to be stringified.
        """
        if self.converter and value:
            return self.converter(value)
        return value
