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

from flask import Blueprint, request, current_app, make_response
from httplib import OK, INTERNAL_SERVER_ERROR
import json
import logging as log
from lsst.webservcommon import renderJsonResponse
from sqlalchemy.exc import SQLAlchemyError

dbREST = Blueprint('dbREST', __name__, template_folder='dbserv')


@dbREST.route('/', methods=['GET'])
def getRoot():
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if fmt == 'text/html':
        return "LSST Database Service v0 here. I currently support: " \
               "<a href='query'>/query</a>."
    return "LSST Database Service v0 here. I currently support: /query."

_error = lambda exception, message: {"exception": exception, "message": message}
_vector = lambda results: {"results": results}


@dbREST.route('/query', methods=['GET'])
def getQuery():
    '''If sql is not passed, it lists quries running for a given user.
       If sql is passed, it runs a given query.'''
    if 'sql' in request.args:
        sql = request.args.get('sql').encode('utf8')
        try:
            engine = current_app.config["default_engine"]
            results = [[i for i in result] for result in engine.execute(sql)]
            status_code = OK
            response = _vector(results)
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
