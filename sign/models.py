from django.db import models


# 数据模型模块
# Create your models here.
# 发布会表
class Event(models.Model):
    objects = models.Manager()
    # 发布会标题
    name = models.CharField(max_length=100)
    # 参加人数最大限制
    limit = models.IntegerField()
    #  状态
    status = models.BooleanField()
    #  地址
    address = models.CharField(max_length=200)
    #  发布会时间
    start_time = models.DateTimeField('events time')
    #  创建时间（自动获取当前时间）
    create_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# 嘉宾表
class Guest(models.Model):
    objects = models.Manager()
    # 关联发布会id, on_delete设置主表删除连带从表数据
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    # 姓名
    realname = models.CharField(max_length=100)
    # 手机号
    phone = models.CharField(max_length=16)
    # 邮箱
    email = models.EmailField()
    # 签到状态
    sign = models.BooleanField()
    # 创建时间（自动获取当前时间）
    create_time = models.DateTimeField(auto_now=True)


class Meta:
    unique_together = ("event", "phone")

    def __str__(self):
        return self.realname
