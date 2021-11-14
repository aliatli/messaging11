import json
import unittest

import common


# TODO:
#  mock persistency layer and test queries
#  find a way to mock tcp/ip stack for the receiver

class QueryBuilderTest(unittest.TestCase):

    def test_default_filter(self):
        query_string = '{"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"", "DIRECTION":"BOTH"}'
        self.assertEqual(True, common.check_valid_json(query_string) and common.check_valid_query(query_string))

    def test_allow_positive_integers(self):
        query_string = '{"HISTORY_DEPTH":"0", "SEARCH_STRING":"", "DIRECTION":"BOTH"}'
        self.assertEqual(False, common.check_valid_query(query_string))

        query_string = '{"HISTORY_DEPTH":"-1", "SEARCH_STRING":"", "DIRECTION":"BOTH"}'
        self.assertEqual(False, common.check_valid_query(query_string))

    def test_direction(self):
        query_string = '{"HISTORY_DEPTH":"1", "SEARCH_STRING":"", "DIRECTION":"BOTH"}'
        self.assertEqual(True, common.check_valid_query(query_string))
        query_string = '{"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"", "DIRECTION":"UP"}'
        self.assertEqual(True, common.check_valid_query(query_string))
        query_string = '{"HISTORY_DEPTH":"100", "SEARCH_STRING":"", "DIRECTION":"DOWN"}'
        self.assertEqual(True, common.check_valid_query(query_string))
        query_string = '{"HISTORY_DEPTH":"100", "SEARCH_STRING":"", "DIRECTION":"OWN"}'
        self.assertEqual(False, common.check_valid_query(query_string))

    def test_nonall(self):
        query_string = '{"HISTORY_DEPTH":"ALLL", "SEARCH_STRING":"", "DIRECTION":"BOTH"}'
        self.assertEqual(False, common.check_valid_query(query_string))

    def test_unicode_search(self):
        query_string = '{"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"اَلْعَرَبِيَّةُ", "DIRECTION":"BOTH"}'
        self.assertEqual(True, common.check_valid_query(query_string))

    def test_escape_quotes(self):
        query_string = '{"HISTORY_DEPTH":"ALL", "SEARCH_STRING":"\\"string\\"", "DIRECTION":"BOTH"}'
        self.assertEqual(True, common.check_valid_json(query_string))
        query = json.loads(query_string)
        self.assertEqual("\"string\"", query['SEARCH_STRING'])

