# coding:utf-8

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
import time

from sign.models import Event, Guest


def add_event(request):
    """ 添加发布会接口 """

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


def get_event_list(request):
    """ 发布会查询接口，提供id和name两种查询方式 """

    # 获取请求的参数
    eid = request.GET.get('eid', '')
    name = request.GET.get('name', '')

    # 判断参数是否合法
    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': '参数不能都为空'})

    # 使用id查询时
    if eid != '':
        # 定义一个变量，存放结果
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': '找不到对应的event'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time

            return JsonResponse({'status': 200, 'message': 'success', 'data': event})

    # 使用name查询时
    if name != '':
        # 定义一个变量，存放结果
        datas = []
        try:
            result = Event.objects.filter(name__contains=name)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10023, 'message': '找不到对应的event'})
        else:
            event = {}
            for r in result:
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)

            return JsonResponse({'status': 200, 'message': 'success', 'data': datas})


def add_guest(request):
    """ 嘉宾添加接口 """

    # 1、获取请求对应的所有字段，不加sign和create_time是因为要直接指定
    eid = request.POST.get("eid", '')
    realname = request.POST.get("realname", '')
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')

    # 2、判断请求的字段是否符合要求
    if eid == '' or realname == '' or phone == '' or email == '':
        return JsonResponse({'status': 10021, 'message': '参数不能为空！'})

    # 3、所有参数都正常，先按id执行查询是否已经存在
    result = Event.objects.filter(id=eid)
    # 如果查不到结果
    if not result:
        return JsonResponse({'status': 10022, 'message': 'event id 不存在'})

    # 4、存在，判断状态
    result = Guest.objects.filter(id=eid).status
    if not result:
        return JsonResponse({'status': 10023, 'message': 'event status 不可用'})

    # 5、id和status都没问题，判断人数限制问题
    event_limit = request.POST.get(id=eid).limit
    guests = Guest.objects.filter(event_id=eid)

    if len(guests) >= event_limit:
        return JsonResponse({'status': 10024, 'message': '发布会限制人数已达上限，添加失败'})

    # 6、最后判断当前时间发布会是否已开始
    event_time = Event.objects.get(id=eid).start_time
    etime = str(event_time).split('.')[0]
    # 根据fmt的格式把一个时间字符串解析为时间元组
    timeArray = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
    # 接受时间元组并返回时间戳
    e_time = int(time.mktime(timeArray))

    # 当前时间，time.time()返回当前时间的时间戳
    now_time = str(time.time())
    ntime = now_time.split('.')[0]
    n_time = int(ntime)

    # 7、如果当前时间超过发布会的开始时间
    if n_time >= e_time:
        return JsonResponse({'status': 10025, 'message': '已超过发布会的开始时间'})

    # 8、都没问题的话
    try:
        Guest.objects.create(event_id=int(eid), realname=realname, phone=phone, email=email, sign='0')
    # 如果时间插入报错
    except IntegrityError as e:
        return JsonResponse({'status': 10026, 'message': '用户的手机号重复了'})

    # 如果都没问题，就插入成功
    return JsonResponse({'status': 200, 'message': '添加嘉宾成功'})


def get_guest_list(request):
    """ 嘉宾查询接口，提供eid和phone两种查询方式 """

    # 获取请求的参数
    eid = request.GET.get('eid', '')
    phone = request.GET.get('phone', '')

    # 判断参数是否合法
    if eid == '':
        return JsonResponse({'status': 10021, 'message': 'eid和phone不能全部为空'})

    # 使用eid查询时
    if eid != '' and phone == '':
        # 定义一个变量，存放所有嘉宾
        guests = []
        try:
            result = Guest.objects.filter(event_id=eid)
        # 如果不存在结果
        except not result:
            return JsonResponse({'status': 10022, 'message': '该发布会不存在或者暂时还没有嘉宾'})
        for re in result:
            guest = {'realname': re.realname, 'phone': re.phone, 'email': re.email, 'sign': re.sign,
                     'create_time': re.create_time}
            guests.append(guest)

        return JsonResponse({'status': 200, 'message': 'success', 'data': guests})

    # 使用eid和phone查询时
    if eid != '' and phone != '':
        try:
            result = Guest.objects.get(event_id=eid, phone=phone)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10023, 'message': 'eid或者phone填写错误'})

        # 都没问题
        guest = {'realname': result.realname, 'phone': result.phone, 'email': result.emai, 'sign': result.sign,
                 'create_time': result.create_time}
        return JsonResponse({'status': 200, 'message': 'success', 'data': guest})


def user_sign(request):
    """ 嘉宾签到接口 """

    # 获取请求的参数
    eid = request.POST.get('eid', '')
    phone = request.POST.get('phone', '')

    # 签到必须两个字段都存在
    if eid == '' or phone == '':
        return JsonResponse({'status': 10021, 'message': 'eid和phone不能为空'})

    # eid和phone都存在时
    result = Event.objects.filter(id=eid)
    # 不存在结果
    if not result:
        return JsonResponse({'status': 10022, 'message': '该发布会不存在'})

    result = Event.objects.filter(id=eid).status
    # 发布会还未开始不可用
    if not result:
        return JsonResponse({'status': 10023, 'message': '该发布会还未开始'})

    # 6、最后判断当前时间发布会是否已开始
    event_time = Event.objects.get(id=eid).start_time
    etime = str(event_time).split('.')[0]
    # 根据fmt的格式把一个时间字符串解析为时间元组
    timeArray = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
    # 接受时间元组并返回时间戳
    e_time = int(time.mktime(timeArray))

    # 当前时间，time.time()返回当前时间的时间戳
    now_time = str(time.time())
    ntime = now_time.split('.')[0]
    n_time = int(ntime)

    # 7、如果当前时间超过发布会的开始时间
    if n_time >= e_time:
        return JsonResponse({'status': 10024, 'message': '已超过发布会的开始时间'})

    # 8、时间满足条件时，检查手机号是否存在
    phone = Guest.objects.get(phone=phone)
    if not phone:
        return JsonResponse({'status': 10025, 'message': '该手机号不存在'})

    # 9、发布会和手机号都没问题的时候，检查是否已经签到过
    sign = Guest.objects.get(eid=eid, phone=phone).sign
    if not sign:
        return JsonResponse({'status': 10026, 'message': '该嘉宾已经签到过'})

    # 如果都没问题，就执行签到
    Guest.objects.get(eid=eid, phone=phone).update(sign='1')
    return JsonResponse({'status': 200, 'message': '签到成功'})
