# coding:utf-8
import base64
from django.contrib import auth as django_auth
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from sign.models import Event


def user_auth(request):
    """ 用户认证 """
    # 本次 HTTP 请求的 Header 信息，得到的数据是这样的：Basic YWRtaW46YWRtaW4xMjM0NTY=
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    # 拆分后的数据是这样的：['Basic', 'YWRtaW46YWRtaW4xMjM0NTY=']
    auth = get_http_auth.split()

    try:
        # 取出 list 中的加密串，通过 base64 对加密串进行解码得到的数据是：('admin', ':', 'admin123456')
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
    except IndexError:
        return "尝试解码header里面的加密认证信息失败"

    # 取出元组中对应的用户 id 和密码。最终于数据： admin	admin123456
    userid, password = auth_parts[0], auth_parts[2]

    # 调用 Django 的认证模块，对得到 Auth 信息进行认证
    user = django_auth.authenticate(username=userid, password=password)
    if user is not None and user.is_active:
        django_auth.login(request, user)
        return "重新认证success"
    else:
        return "重新认证fail"


def get_event_list(request):
    """ 发布会查询接口---增加用户认证，产生类似于 @login_required 的效果"""
    # 调用认证函数，拿到认证结果
    auth_result = user_auth(request)
    if auth_result == "null":
        return JsonResponse({'status': 10011, 'message': '用户认证信息为空'})
    if auth_result == "fail":
        return JsonResponse({'status': 10012, 'message': '用户认证失败'})

    # 发布会id
    eid = request.GET.get("eid", "")
    # 发布会名称
    name = request.GET.get("name", "")

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
            return JsonResponse({'status': 10022, 'message': '找不到eid %s 对应的发布会' % eid})
        else:
            event['id'] = eid
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time

            return JsonResponse({'status': 200, 'message': '查询发布会成功', 'data': event})

    # 使用name查询时
    if name != '':
        # 定义一个变量，存放结果
        datas = []
        result = Event.objects.filter(name__contains=name)
        if result:
            for r in result:
                event = {'id': r.id, 'name': r.name, 'limit': r.limit, 'status': r.status, 'address': r.address,
                         'start_time': r.start_time}
                datas.append(event)
            return JsonResponse({'status': 200, 'message': '查询发布会成功', 'data': datas})
        else:
            return JsonResponse({'status': 10023, 'message': '找不到name %s 对应的event' % name})


def get_guest_list(request):
    """ 嘉宾查询接口----AES算法 """
    pass
