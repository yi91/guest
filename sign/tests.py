import unittest
from datetime import datetime

from django.contrib.auth.models import User

from sign.models import Event, Guest
from django.test import TestCase, Client


# Create your tests here.
# 自动化测试模块
# 数据库的测试，测试发布会和嘉宾模型
class ModelTest(TestCase):

    def setUp(self):
        # 初始化获取两个对象
        Event.objects.create(id=1, name="oneplus3event", status=True, limit=2000,
                             address='shenzhen', start_time='2016-08-31 02:18:22')
        Guest.objects.create(id=1, event_id=1, realname='alen', phone='13711001101',
                             email='alen@mail.com', sign=False)

    def tearDown(self):
        pass

    def test_event_model(self):
        result = Event.objects.get(name="oneplus3event")
        self.assertEqual(result.address, 'shenzhen')

    # 换一种断言写法
    @staticmethod
    def test_guest_model():
        g1 = Guest.objects.filter(realname='alen')
        if g1:
            print('嘉宾alen验证成功！')
        else:
            print('嘉宾alen验证失败！')


# 页面的测试
class IndexPageTest(TestCase):
    """ 测试登录index首页 """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_index_page_renders_index_template(self):
        """ 测试index视图 """
        # client.get()方法从 TestCase 父类继承而来，用于请求一个路径
        response = self.client.get("/index/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.template_pages")


# 不继承TestCase就无法使用TestCase的断言，也无法找到类下的用例
class LoginActionTest(TestCase):
    """ 测试登陆函数 """

    def setUp(self):
        # 获取客户端实例，模拟发送请求
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        self.c = Client()

    def tearDown(self):
        pass

    def test_login_action_username_password_null(self):
        """ 用户名和密码为空 """
        test_data = {"username": "", "password": ""}
        resp = self.c.post("/login_action/", test_data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('用户名或密码错误！', resp.content)

    def test_login_action_username_password_error(self):
        """ 用户名或密码错误 """
        test_data = {"username": "111", "password": "admin123456"}
        resp = self.c.post("/login_action/", test_data)
        self.assertTemplateUsed(resp, "index.template_pages")

    def test_login_action_success(self):
        """ 登录成功 """
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.c.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)


class EventManageTest(TestCase):
    # 测试发布会的相关功能，需要关闭登录校验@login_required
    def setUp(self):
        self.c = Client()
        Event.objects.create(id=2, name='xiaomi5', limit=2000, status=True, address='beijing',
                             start_time=datetime(2016, 8, 10, 14, 0, 0))

    def tearDown(self):
        pass

    def test_event_manage_success(self):
        """ 测试发布会：xiaomi5 添加成功"""
        resp = self.c.post("/event_manage/")
        self.assertEqual(resp.status_code, 200)
        # 使用byte格式判断，不加会报错
        self.assertIn(b"xiaomi5", resp.content)

    def test_event_manage_search_success(self):
        """ 测试发布会搜索成功 """
        test_data = {"name": 'xiaomi5'}
        resp = self.c.get("/search_name/", test_data)
        self.assertEqual(resp.status_code, 200)
        # 使用byte格式判断，不加会报错
        self.assertIn(b"beijing", resp.content)


class GuestManageTest(TestCase):
    """ 嘉宾管理 """

    def setUp(self):
        # 两条数据并不会直接插入数据库
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1,
                             start_time=datetime(2016, 8, 10, 14, 0, 0))
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0,
                             event_id=1)
        # 使用客户端发起请求
        self.c = Client()

    def tearDown(self):
        pass

    def test_guest_manage_success(self):
        """ 测试嘉宾添加成功 """
        resp = self.c.get("/guest_manage/")
        self.assertEqual(resp.status_code, 302)
        # 思考：为啥会跳转拿不到返回值
        self.assertIn(b"alen", resp.content)

    def test_guest_manage_search_success(self):
        """ 测试嘉宾手机号搜索成功 """
        resp = self.c.post("/search_phone/", {"phone": "18611001100"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"alen", resp.content)


class SignIndex(TestCase):
    """ 测试签到页面 """

    def test_sign_index_page_renders_index_template(self):
        """ 测试sign_index视图 """
        response = self.client.get('/sign_index/1/')
        self.assertEqual(response.status_code, 404)
        # self.assertTemplateUsed(response, 'sign_index.html')


class SignIndexActionTest(TestCase):
    """ 测试发布会签到 """

    def setUp(self):
        Event.objects.create(id=1, name="xiaomi5", limit=2000, address='beijing', status=1,
                             start_time='2017-8-10 12:30:00')

        Event.objects.create(id=2, name="oneplus4", limit=2000, address='shenzhen', status=1,
                             start_time='2017-6-10 12:30:00')
        Guest.objects.create(realname="alen", phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname="una", phone=18611001101, email='una@mail.com', sign=1, event_id=2)
        self.c = Client()

    def test_sign_index_action_phone_null(self):
        """ 手机号为空 """

        response = self.c.post('/sign_index_action/1/', {"phone": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"phone error.", response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        """ 手机号或发布会id错误 """

        response = self.c.post('/sign_index_action/2/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"event id or phone error.", response.content)

        response = self.c.post('/sign_index_action/19/', {'phone': '13600550955'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not Found', response.content)

    def test_sign_index_action_user_sign_has(self):
        """ 嘉宾已签到 """

        response = self.c.post('/sign_index_action/2/', {"phone": "18611001101"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"user has sign in.", response.content)

    def test_sign_index_action_sign_success(self):
        """ 签到成功 """

        response = self.c.post('/sign_index_action/1/', {"phone": "18611001100"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"sign in success!", response.content)

    def test_sign_off_action_success(self):
        """ 取消签到成功 """
        response = self.c.post('/sign_off_action/2/', {'phone': '13600550755'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'taozi', response.content)
        self.assertIn('取消签到成功！', response.content)


# 不能用下面的方式测试，因为tests是作为整个项目的测试，所以需要python manage.py test来测试
"""
if __name__ == '__main__':
# 构造测试集，指定测试用例
suit = my_unittest.TestSuite()
suit.addTest(ModelTest("test_event_model"))
# suit.addTest(ModelTest("test_div"))
# 执行测试
runner = my_unittest.TextTestRunner()
runner.run(suit)
"""
