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
This is a program for running RESTful LSST Database Server (only).
Use it for tests. It is really meant to run as part of the central
Web Service, e.g., through webserv/bin/server.py

@author  Jacek Becla, SLAC
"""

from flask import Flask, request
from lsst.dbserv import dbREST_v0
import json

app = Flask(__name__)

@app.route('/')
def getRoot():
    return '''Test server for testing db. Try adding /db to URI.
'''

@app.route('/db')
def getDb():
    '''Lists supported versions for /db.'''
    fmt = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    s = '''v0
'''
    if fmt == "text/html":
        return s
    return json.dumps(s)

app.register_blueprint(dbREST_v0.dbREST, url_prefix='/db/v0')

if __name__ == '__main__':
    app.run(debug=True)
