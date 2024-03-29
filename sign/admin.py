from django.contrib import admin
from sign.models import Guest, Event


# admin后台管理系统配置
class EventAdmin(admin.ModelAdmin):
    # 定义要在列表中显示哪些字段
    list_display = ['id', 'name', 'status', 'start_time']
    # 搜索栏
    search_fields = ['name']
    # 过滤器
    list_filter = ['status']


class GuestAdmin(admin.ModelAdmin):
    list_display = ['id', 'realname', 'phone', 'sign', 'event', 'email', 'create_time']
    # 搜索栏
    search_fields = ['realname', 'phone']
    # 过滤器
    list_filter = ['sign']


# 用 EventAdmin 选项注册 Event 模块
admin.site.register(Event, EventAdmin)
admin.site.register(Guest, GuestAdmin)
