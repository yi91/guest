# coding:utf-8
import hashlib
import time

from django.core.exceptions import ValidationError
from django.http import JsonResponse

from sign.models import Event


def user_sign(request):
    """ 用户签名+时间戳 """

    client_time = request.POST.get('time', '')
    client_sign = request.POST.get('sign', '')
    if client_time == '' or client_sign == '':
        return "sign null"

    # 服务器时间戳
    now_time = time.time()  # 1466426831
    server_time = str(now_time).split('.')[0]
    # 获取时间差，超时时间是60秒
    time_difference = int(server_time) - int(client_time)
    if time_difference >= 60:
        return "timeout"

    # 服务的的签名检查
    md5 = hashlib.md5()
    sign_str = client_time + "&Guest-Bugmaster"

    sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
    # 开始加密
    md5.update(sign_bytes_utf8)
    sever_sign = md5.hexdigest()

    if sever_sign != client_sign:
        return "sign error"
    else:
        return "sign right"


def add_event(request):
    sign_result = user_sign(request)
    if sign_result == 'sign null':
        return JsonResponse({'status': 10011, 'message': 'user sign null'})
    elif sign_result == 'timeout':
        return JsonResponse({'status': 10012, 'message': '请求超时，请重试'})
    elif sign_result == 'sign error':
        return JsonResponse({'status': 10013, 'message': 'sign error'})
    else:
        # 1、获取请求对应的所有字段
        eid = request.POST.get("eid", '')
        name = request.POST.get("name", '')
        limit = request.POST.get('limit', '')
        status = request.POST.get('status', '')
        address = request.POST.get('address', '')
        start_time = request.POST.get('start_time', '')

        # 2、判断请求的字段是否符合要求
        if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
            return JsonResponse({'status': 10021, 'message': '参数不能为空！'})

        # 3、所有参数都正常，先按id执行查询是否已经存在
        result = Event.objects.filter(id=eid)
        # 如果查到了结果
        if result:
            return JsonResponse({'status': 10022, 'message': 'event id 已经存在了'})

        # 4、按名称查询是否存在
        result = Event.objects.filter(name=name)
        if result:
            return JsonResponse({'status': 10023, 'message': 'event name 已经存在'})

        # 5、如果id和name都没问题，就准备插入数据
        if status == '':
            status = 1

        try:
            Event.objects.create(id=eid, name=name, limit=limit, address=address, status=int(status),
                                 start_time=start_time)

        except ValidationError as e:
            error = 'start_time格式化错误，请检查'
            return JsonResponse({'status': 10024, 'message': error})

        # 6、如果都没问题，就插入成功
        return JsonResponse({'status': 200, 'message': '添加发布会成功'})


if __name__ == '__main__':
    now_time = time.time()
    print('当前时间戳:' + str(now_time))

    # 转换时间格式
    otherStyleTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_time))
    print('日期格式:' + str(otherStyleTime))
