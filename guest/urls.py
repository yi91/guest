"""guest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path, include
from django.contrib import admin
from sign import views

# 导入sign应用views文件

# 添加index/路径配置
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', views.index),
    re_path(r'^index/$', views.index),
    re_path(r'^accounts/login/$', views.index),
    re_path(r'^index_bak/$', views.index_bak),
    re_path(r'^login_action/$', views.login_action),
    re_path(r'^event_manage/$', views.event_manage),
    re_path(r'^search_name/$', views.search_name),
    re_path(r'^search_phone/$', views.search_phone),
    re_path(r'^guest_manage/$', views.guest_manage),
    re_path(r'^sign_index/(?P<event_id>[0-9]+)/$', views.sign_index),
    re_path(r'^sign_index_action/(?P<event_id>[0-9]+)/$', views.sign_index_action),
    re_path(r'^sign_off_action/(?P<event_id>[0-9]+)/$', views.sign_off_action),
    re_path(r'^logout/$', views.logout),
    # 配置接口的二级路径
    re_path(r'^api/', include('sign.urls', namespace="sign")),
]
