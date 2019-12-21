from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from sign.models import Event, Guest


@login_required
def index_bak(request):
    return HttpResponse("Hello Django!")


def index(request):
    return render(request, "index.template_pages")


# 登录动作
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # 启用Django 认证登录
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # 登录
            request.session['user'] = username
            # 将session信息记录到浏览器
            response = HttpResponseRedirect('/event_manage/')

            return response
        else:
            return render(request, 'index.template_pages', {'error': 'username or password error!'})


'''
        if username == 'admin' and password == 'admin123':
            # return HttpResponse('login success!')

            # 添加浏览器cookie return response
            # response.set_cookie('user', username, 3600)

            # 将 session 信息记录到浏览器
            request.session['user'] = username

            # 换一种写法，对路径进行重定向
            return HttpResponseRedirect('/event_manage/')
        else:
            return render(request, 'index.template_pages', {'error': 'username or password error!'})
'''


# 发布会管理
# @login_required
def event_manage(request):
    # 读取浏览器cookie
    # username = request.COOKIES.get('user', '')

    # 读取浏览器 session
    username = request.session.get('user', '')
    # 查询所有发布会对象
    event_list = Event.objects.all()

    return render(request, "event_manage.template_pages", {"user": username, "events": event_list})


# 发布会名称搜索
# @login_required
def search_name(request):
    username = request.session.get('user', '')
    name_search = request.GET.get("name", "")
    event_list = Event.objects.filter(name__contains=name_search)
    return render(request, "event_manage.template_pages", {"user": username, "events": event_list})


# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()

    # 添加分页器的代码
    paginator = Paginator(guest_list, 5)
    page = request.GET.get('page')

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.template_pages", {"user": username, "guests": contacts})


# 嘉宾手机号搜索
# @login_required
def search_phone(request):
    phone = request.session.get('phone', '')
    phone_search = request.GET.get("phone", "")
    # 注意filter的参数phone__contains，必须是表字段内的
    guest_list = Guest.objects.filter(phone__contains=phone_search)

    # 添加分页器的代码
    paginator = Paginator(guest_list, 5)
    page = request.GET.get('page')

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(request, "guest_manage.template_pages", {"phone": phone, "guests": contacts})


# 签到页面
@login_required
def sign_index(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'sign_index.template_pages', {'event': event})


# 签到动作
@login_required
def sign_index_action(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone', '')

    # 判断用户输入的手机号是否存在
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.template_pages', {'event': event, 'hint': 'phone error.'})

    # 通过手机和发布会 id 两个条件来查询 Guest
    result = Guest.objects.filter(phone=phone, event_id=event_id)
    if not result:
        return render(request, 'sign_index.template_pages', {'event': event, 'hint': 'eventid or phone error.'})

    # 判断该手机号的签到状态是否为 1
    result = Guest.objects.get(phone=phone, event_id=event_id)
    if result.sign:
        return render(request, 'sign_index.template_pages', {'event': event, 'hint': "user has sign in."})
    else:
        Guest.objects.filter(phone=phone, event_id=event_id).update(sign='1')

    return render(request, 'sign_index.template_pages', {'event': event, 'hint': 'sign in success!', 'guest': result})


# 取消签到
@login_required()
def sign_off_action(request, event_id):
    # 读取浏览器session
    username = request.session.get('user', '')
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone', '')
    guest_list = Guest.objects.filter(event_id=event_id, sign='1').order_by('id')
    # 第一步判断手机号
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.template_pages',
                      {'user': username, 'event': event, '提示2': '该手机号不存在！', 'guests': guest_list})
    # 第二步判断手机号和发布会的唯一性
    result = Guest.objects.filter(phone=phone, event_id=event_id)
    if not result:
        return render(request, 'sign_index.template_pages',
                      {'user': username, 'event': event, '提示2': '该用户未参加此次发布会！', 'guests': guest_list})
    # 第三步判断是否重复签到
    result = Guest.objects.get(phone=phone, event_id=event_id)
    if not result.sign:
        return render(request, 'sign_index.template_pages',
                      {'user': username, 'event': event, '提示2': '该手机号尚未签到！', 'guests': guest_list})

    else:
        Guest.objects.filter(phone=phone, event_id=event_id).update(sign='0')
        return render(request, 'sign_index.template_pages',
                      {'user': username, 'event': event, '提示2': '取消签到成功！', 'guest2': result, 'guests': guest_list})


# 退出登录
@login_required
def logout(request):
    auth.logout(request)  # 退出登录
    response = HttpResponseRedirect('/index/')
    return response
