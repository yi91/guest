# -*- coding: utf-8 -*-
import requests
import unittest


class SearchEventTest(unittest.TestCase):
    """ 发布会查询接口测试 """

    def setUp(self):
        self.url = 'http://127.0.0.1:8000/api/search_event/'

    def test_search_event(self):
        """ 测试发布会查询接口 """
        response = requests.post(self.url, params={'eid': ''})
        result = response.json()
        print(result)
        self.assertEqual(result['status'], '10021')


if __name__ == '__main__':
    unittest.main()
