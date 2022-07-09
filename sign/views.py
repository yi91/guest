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
    return render(request, "index.html")


# 登录动作（前台浏览器）
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # 启用Django 认证登录
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            # 登录
            auth.login(request, user)
            # 将session信息记录到浏览器
            request.session['user'] = username
            # 页面重定向到发布会页面
            response = HttpResponseRedirect('/event_manage/')
            return response
        else:
            return render(request, 'index.html', {'error': 'username or password error!'})
    else:
        return render(request, 'index.html', {'error': 'username or password error!'})


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
            return render(request, 'index.html', {'error': 'username or password error!'})
'''


# 发布会管理（后台服务器）
# @login_required
def event_manage(request):
    # 读取浏览器cookie
    # username = request.COOKIES.get('user', '')

    # 读取浏览器 session
    username = request.session.get('user', '')
    # 查询所有发布会对象，并按id升序
    event_list = Event.objects.all().order_by('id')

    # 分页
    paginator = Paginator(event_list, 5)
    page_num = request.GET.get('page')
    try:
        contacts = paginator.page(page_num)
    except PageNotAnInteger:
        # 如果页面不是整数，默认跳转第一页
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果页面超过9999，默认跳转最后一页
        contacts = paginator.page(paginator.num_pages)

    return render(request, "event_manage.html", {"user": username, "events": contacts})


# 发布会名称搜索
# @login_required
def search_name(request):
    username = request.session.get('user', '')
    search_text = request.GET.get("name", "")
    event_list = Event.objects.filter(name__contains=search_text)

    return render(request, "event_manage.html", {"user": username, "events": event_list})


# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all().order_by('id')

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

    return render(request, "guest_manage.html", {"user": username, "guests": contacts})


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

    return render(request, "guest_manage.html", {"phone": phone, "guests": contacts})


# 签到页面
@login_required
def sign_index(request, event_id):
    # 读取浏览器session
    username = request.session.get('user', '')

    event = get_object_or_404(Event, id=event_id)
    # 获取所有已签到嘉宾信息给前端展示
    guest_list = Guest.objects.filter(event_id=event_id, sign='1').order_by('id')

    return render(request, 'sign_index.html', {'user': username, 'event': event, 'guests': guest_list})


# 签到动作
@login_required
def sign_index_action(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    phone = request.POST.get('phone', '')

    # 判断用户输入的手机号是否存在
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': '手机号 %s 不存在，请检查！' % phone})

    # 通过手机和发布会 id 两个条件来查询 Guest
    result = Guest.objects.filter(phone=phone, event_id=event_id)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': '该嘉宾未参加此次发布会，请检查！'})

    # 判断该手机号的签到状态，1 代表已签到，0 代表未签到，
    if result.sign:
        return render(request, 'sign_index.html', {'event': event, 'hint': "嘉宾已签到，无需重复签到。"})
    else:
        result.update(sign='1')
        return render(request, 'sign_index.html', {'event': event, 'hint': '签到成功！', 'guest': result})


# 取消签到
@login_required()
def sign_off_action(request, event_id):
    phone = request.POST.get('phone', '')

    # 第一步判断手机号
    result = Guest.objects.filter(phone=phone)
    if not result:
        # 因为sign_index页面会自动获取user和event信息，所以下面不再重复写
        return render(request, 'sign_index.html', {'hint0': '该手机号 %s 不存在！' % phone})
    # 第二步判断手机号和发布会的唯一性
    result = Guest.objects.filter(phone=phone, event_id=event_id)
    if not result:
        return render(request, 'sign_index.html', {'hint0': '该嘉宾未参加此次发布会！'})
    # 第三步判断是否已取消签到
    if result.sign:
        result.update(sign='0')
        return render(request, 'sign_index.html', {'hint0': '取消签到成功！手机号 %s' % phone})
    else:
        return render(request, 'sign_index.html', {'hint0': '该手机号 %s 未签到，无需取消！' % phone})


# 退出登录
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response
