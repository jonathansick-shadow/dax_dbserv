import json
import unittest
from flask import Flask
from lsst.dax.dbserv import dbREST_v0
from mock import MagicMock

import MySQLdb


class MockResults(list):

    def __init__(self, seq=(), description=None):
        super(MockResults, self).__init__(seq)
        self.cursor = MagicMock()
        self.cursor.description = description
        self.cursor.description_flags = [0 for _ in description]


def mysql_desc(col):
    name = str(col)
    typ = MySQLdb.constants.FIELD_TYPE.DOUBLE
    if isinstance(col, str):
        typ = MySQLdb.constants.FIELD_TYPE.STRING
    return name, typ, None, None, None, 0, None, None


class TestMySqlQuery(unittest.TestCase):

    queries = {
        "SELECT 1": [[1]],
        "SELECT 1, 2": [[1, 2]],
        "SELECT 1, 2, 3": [[1, 2, 3]],
        "SELECT 'foo'": [["foo"]],
        "SELECT 'foo', 'bar'": [["foo", "bar"]],
        "SELECT 1, 'foo'": [[1, "foo"]],
    }

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.mock_engine = MagicMock()
        self.app.config['default_engine'] = self.mock_engine
        self.app.register_blueprint(dbREST_v0.dbREST, url_prefix='/db/v0')

        def side_effect(arg):
            arg = str(arg)   # This is actually a sqlalchemy.text object, convert to string
            return MockResults(self.queries[arg], [mysql_desc(c) for c in self.queries[arg][0]])

        self.mock_engine.execute.side_effect = side_effect

    def test_basic_queries_json(self):

        for query, results in self.queries.items():
            resp = self.client.get("/db/v0/query?sql=" + query)
            self.assertEqual(json.loads(resp.data)["results"], results)

    def test_basic_queries_html(self):

        for query, results in self.queries.items():
            resp = self.client.get("/db/v0/query?sql=" + query, headers={"accept": "text/html"})
            expected_row = "<td>" + "</td><td>".join([str(i) for i in results[0]]) + "</td>"
            self.assertIn(expected_row, resp.data)

if __name__ == '__main__':
    unittest.main()
