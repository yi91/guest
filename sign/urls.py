# coding:utf-8

from django.urls import re_path
from sign import views_if, views_if_sec, views_if_md5
# 二级路径，供接口使用
urlpatterns = [
    # guest system interface:
    # ex : /api/add_event/
    re_path(r'^add_event/', views_if.add_event, name='add_event'),
    re_path(r'^sec_add_event/', views_if_md5.add_event, name='add_event'),
    # ex : /api/add_guest/
    re_path(r'^add_guest/', views_if.add_guest, name='add_guest'),
    # ex : /api/get_event_list/
    re_path(r'^get_event_list/', views_if.get_event_list, name='get_event_list'),
    re_path(r'^sec_get_event_list/', views_if_sec.get_event_list, name='get_event_list'),
    # ex : /api/get_guest_list/
    re_path(r'^get_guest_list/', views_if.get_guest_list, name='get_guest_list'),
    # ex : /api/user_sign/
    re_path(r'^user_sign/', views_if.user_sign, name='user_sign'),
]
