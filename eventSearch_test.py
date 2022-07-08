import unittest
import requests


class EventSearchTest(unittest.TestCase):
    """ 测试发布会搜索功能 """
    def setUp(self):
        self.url = 'http://127.0.0.1:8000/api/get_event_list/'

    def tearDown(self):
        pass

    def test_eid_name_null(self):
        """ 测试请求参数eid和name都为空 """
        r = requests.get(self.url, params={'eid': '', 'name': ''})
        print(r.json())
        self.assertEqual(r.json()['status'], 10021)
        self.assertIn('参数不能都为空', r.json()['message'])

    def test_search_by_eid_fail(self):
        """ 测试通过eid查询发布会失败 """
        r = requests.get(self.url, params={'eid': '99'})
        print(r.json())
        self.assertEqual(r.json()['status'], 10022)
        self.assertIn('找不到', r.json()['message'])

    def test_search_by_eid_success(self):
        """ 测试通过eid查询发布会成功 """
        r = requests.get(self.url, params={'eid': '1'})
        print(r.json())
        self.assertEqual(r.json()['status'], 200)

    def test_search_by_name_fail(self):
        """ 测试通过name查询发布会失败 """
        r = requests.get(self.url, params={'name': '1234'})
        print(r.json())
        self.assertEqual(r.json()['status'], 10023)

    def test_search_by_name_success(self):
        """ 测试通过name查询发布会成功 """
        r = requests.get(self.url, params={'name': '魅族'})
        print(r.json())
        self.assertEqual(r.json()['status'], 200)

    def test_search_by_eid_name(self):
        """ 测试同时有eid和name的情况 """
        r = requests.get(self.url, params={'eid': '4', 'name': '魅族'})
        print(r.json())
        self.assertEqual(r.json()['status'], 200)


if __name__ == '__main__':
    unittest.main()
