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
        return JsonResponse({'status': 10021, 'message': '所有参数不能为空！'})

    # 3、所有参数都正常，先按id执行查询是否已经存在
    result = Event.objects.filter(id=eid)
    # 如果查到了结果
    if result:
        return JsonResponse({'status': 10022, 'message': 'event id 已经存在了'})

    # 4、按名称查询是否存在
    eve = Event.objects.filter(name=name)
    if eve:
        return JsonResponse({'status': 10023, 'message': 'event name 已经存在'})

    # 5、如果id和name都没问题，就准备插入数据，布尔类型只有两种，false(0，null)或者 true（非0且非null）
    if status != '0' and status != '':
        status = 1
        try:
            Event.objects.create(id=eid, name=name, limit=limit, address=address, status=status,
                                 start_time=start_time)
        except ValidationError:
            error = 'start_time格式化错误，时间格式必须是YYYY-MM-DD HH:MM:SS'
            return JsonResponse({'status': 10024, 'message': error})
    else:
        try:
            # status为 0 的直接插入数据
            Event.objects.create(id=eid, name=name, limit=limit, status=0,
                                 address=address, start_time=start_time)
        except ValidationError:
            error = 'start_time格式错误，时间格式必须是YYYY-MM-DD HH:MM:SS'
            return JsonResponse({'status': 10025, 'massage': error})
    # 没报错，最后肯定成功
    return JsonResponse({'status': 200, 'message': 'eid为 %s 的发布会添加成功' % eid})


def get_event_list(request):
    """ 发布会查询接口，提供id和name以及组合三种查询方式 """

    # 获取请求的参数
    eid = request.GET.get('eid', '')
    name = request.GET.get('name', '')

    # 判断参数是否合法
    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': 'event的id 和 name参数不能都为空'})

    # 使用id查询时
    if eid != '':
        # 定义一个变量，存放结果
        event = {}
        try:
            # get方法需要包裹在try里面
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022, 'message': '找不到对应id的发布会'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time

            return JsonResponse({'status': 200, 'message': '该eid %s 查询发布会成功' % eid, 'data': event})

    # 使用name查询时
    if name != '':
        # 定义一个变量，存放结果
        datas = []
        # filter方法不会报错，不需要try
        events = Event.objects.filter(name__contains=name)
        if events:
            for e in events:
                event = {'name': e.name, 'limit': e.limit, 'status': e.status, 'address': e.address,
                         'start_time': e.start_time}
                datas.append(event)
            return JsonResponse({'status': 200, 'message': '查询发布会成功', 'data': datas})
        else:
            return JsonResponse({'status': 10023, 'message': '找不到对应name的发布会'})


def add_guest(request):
    """ 嘉宾添加接口 """

    # 1、获取请求对应的所有字段，不加sign和create_time是因为sign要直接指定，create_time默认当前时间
    eid = request.POST.get("eid", '')
    realname = request.POST.get("realname", '')
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')

    # 2、判断请求的字段是否符合要求
    if eid == '' or realname == '' or phone == '' or email == '':
        return JsonResponse({'status': 10021, 'message': 'guest所有参数不能为空！'})

    # 3、所有参数都正常，先按id执行查询发布会是否已经存在
    result = Event.objects.filter(id=eid)
    # 如果查不到结果
    if not result:
        return JsonResponse({'status': 10022, 'message': '嘉宾参加的发布会不存在'})

    # 4、存在，判断发布会状态，1 代表发布会可用，0 不可用
    if not result.status:
        return JsonResponse({'status': 10023, 'message': '嘉宾不允许参加 %s （不可用）' % result.name})

    # 5、id和status都没问题，判断人数限制问题，发布会实际参加人数 < 发布会limit
    guests = Guest.objects.filter(event_id=eid)

    if len(guests) >= result.limit:
        return JsonResponse({'status': 10024, 'message': '发布会人数已达上限 %s ，添加失败' % result.limit})

    # 6、最后判断当前时间发布会是否已开始
    etime = str(result.start_time).split('.')[0]
    # 根据fmt的格式把一个时间字符串解析为时间元组
    timeArray = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
    # 接受时间元组并返回时间戳
    e_time = int(time.mktime(timeArray))

    # 当前时间，time.time()返回当前时间的时间戳
    now_time = str(time.time())
    ntime = now_time.split('.')[0]
    n_time = int(ntime)

    # 6.1、比较两个时间戳的整数部分，如果当前时间超过发布会的开始时间
    if n_time >= e_time:
        return JsonResponse({'status': 10025, 'message': '该 %s 已经开始或结束，无法参加' % result.name})

    # 7、判断手机号是否重复
    try:
        Guest.objects.create(event_id=int(eid), realname=realname, phone=phone, email=email, sign=0)
    # 如果插入报错
    except IntegrityError as e:
        return JsonResponse({'status': 10026, 'message': '嘉宾的手机号 %s 已经存在' % phone})

    # 如果都没问题，就插入成功
    return JsonResponse({'status': 200, 'message': '添加嘉宾成功'})


def get_guest_list(request):
    """ 嘉宾查询接口，提供eid和phone以及组合三种查询方式 """

    # 获取请求的参数
    eid = request.GET.get('eid', '')
    phone = request.GET.get('phone', '')

    # 判断参数是否合法
    if eid == '' and phone == '':
        return JsonResponse({'status': 10021, 'message': '嘉宾查询的eid和phone不能全部为空'})

    # 使用eid查询时
    if eid != '' and phone == '':
        # 定义一个变量，存放所有嘉宾
        guests = []
        result = Guest.objects.filter(event_id=eid)
        if result:
            for re in result:
                guest = {'eid': eid, 'realname': re.realname, 'phone': re.phone, 'email': re.email,
                         'sign': re.sign, 'create_time': re.create_time}
                guests.append(guest)
            return JsonResponse({'status': 200, 'message': 'eid查询嘉宾成功', 'data': guests})
        else:
            return JsonResponse({'status': 10022, 'message': '该发布会id尚未有嘉宾参加'})

    # 使用phone查询时
    if eid == '' and phone != '':
        guest = []
        try:
            result = Guest.objects.get(phone=phone)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10023, 'message': '该手机号所属嘉宾尚未参加任何发布会'})
        else:
            # 查到嘉宾
            for g in result:
                gue = {'event_id': g.event_id, 'realname': g.realname, 'phone': g.phone, 'email': g.emai,
                       'sign': g.sign, 'create_time': g.create_time}
                guest.append(gue)
            return JsonResponse({'status': 200, 'message': '手机号查询嘉宾成功', 'data': guest})

    # 使用eid和phone一起查询，结果应该只有一条
    result = Guest.objects.filter(event_id=eid, phone=phone)
    if result:
        return JsonResponse({'status': 200, 'message': 'eid和手机号查询嘉宾成功', 'data': result})
    else:
        return JsonResponse({'status': 10024, 'message': '该eid %s 和手机号 %s 所属嘉宾信息不存在' % (eid, phone)})


def user_sign(request):
    """ 嘉宾签到接口 """

    # 获取请求的参数
    eid = request.POST.get('eid', '')
    phone = request.POST.get('phone', '')

    # 签到必须两个字段都存在，因为guest表的event和phone具有唯一性
    if eid == '' or phone == '':
        return JsonResponse({'status': 10021, 'message': 'eid或者phone不能为空'})

    # eid和phone都存在时
    result = Event.objects.filter(id=eid)
    # 不存在结果
    if not result:
        return JsonResponse({'status': 10022, 'message': '该发布会eid %s 不存在' % eid})

    # 发布会状态不可用
    if not result.status:
        return JsonResponse({'status': 10023, 'message': '该发布会eid %s 暂不可用' % eid})

    # 6、最后判断当前时间发布会是否已开始
    etime = str(result.start_time).split('.')[0]
    # 根据fmt的格式把一个时间字符串解析为时间元组
    timeArray = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
    # 接受时间元组并返回时间戳
    e_time = int(time.mktime(timeArray))

    # 当前时间，time.time()返回当前时间的时间戳
    now_time = str(time.time())
    ntime = now_time.split('.')[0]
    n_time = int(ntime)

    # 6.1、如果当前时间超过发布会的开始时间
    if n_time >= e_time:
        return JsonResponse({'status': 10024, 'message': '该 %s 已开始，无法参加' % result.name})

    # 7、时间满足条件时，检查手机号是否存在
    g = Guest.objects.filter(event_id=eid, phone=phone)
    if not g:
        return JsonResponse({'status': 10025, 'message': '该手机号不存在'})

    # 9、发布会和手机号都没问题的时候，检查是否已经签到过
    if not g.sign:
        return JsonResponse({'status': 10026, 'message': '该嘉宾已经签到过'})

    # 如果都没问题，就执行签到，这时候get不会报错，所以不用try
    g.update(sign='1')
    return JsonResponse({'status': 200, 'message': '嘉宾 %s 签到成功' % g.realname})
