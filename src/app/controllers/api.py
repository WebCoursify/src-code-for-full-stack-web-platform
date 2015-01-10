from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from django.core.mail import send_mail
from datetime import datetime
from app.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import hashlib
import uuid
import os
from web_dev_tutorial.settings import MEDIA_ROOT, BASE_DIR, EMAIL_HOST_USER

###########
# Helpers #
###########

def md5(stream):
    m = hashlib.md5()
    m.update(stream)
    return m.hexdigest()


def get_logon_user(request):
    return User.objects.get(id=request.session.get('user')['id'])


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)

##############
# Decorators #
##############

def json_view(controller):
    def inner(*args, **kwargs):
        res = controller(*args, **kwargs)
        if isinstance(res, list) or isinstance(res, dict):
            return HttpResponse(json.dumps(res, cls=ComplexEncoder))

        return res
    return inner

def login_required_otherwise_401(controller):
    def inner(*args, **kwargs):
        request = args[0]
        if 'user' not in request.session:
            return HttpResponse('Unauthorized', status=401)
        else:
            user_id = request.session.get('user')['id']
            user = User.objects.find_by_id(user_id)
            if user is None:
                return HttpResponse('Invalid user', status=403)
            return controller(*args, **kwargs)
    return inner


def allow_methods(methods):
    methods = [method.upper() for method in methods]
    def decorator(controller):

        def inner(*args, **kwargs):
            request = args[0]
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)

            return controller(*args, **kwargs)

        return inner
    return decorator

def article_operation(author_required=False):
    def decorator(controller):

        def inner(*args, **kwargs):
            request, article_id = args[0], kwargs['article_id']

            article = Article.objects.filter(id=int(article_id), deleted=0)
            if not article.exists():
                return HttpResponseNotFound('Article Not found')
            article = article[0]
            if author_required:
                if 'user' not in request.session:
                    return HttpResponse('Unauthorized', status=401)
                if request.session.get('user')['id'] != article.author_id:
                    return HttpResponseNotAllowed('Open allowed for author')

            return controller(*args, **kwargs)

        return inner

    return decorator

######################
# Account management #
######################

def write_user_info_to_session(user, request):
    request.session['user'] = {'id': user.id, 'username': user.username, 'avatar': user.avatar}

@csrf_exempt
def login(request):
    email = request.REQUEST.get('email', None)
    password = request.REQUEST.get('password', None)
    if email is None or password is None:
        return HttpResponseBadRequest('email and password required')

    password = md5(password)
    user = User.objects.filter(email=email, password=password, deleted=0)
    if not user.exists():
        return HttpResponse(json.dumps({'error': 'Incorrect email/password'}))

    user = user[0]
    write_user_info_to_session(user, request)

    return HttpResponse(json.dumps({'success': True}))


@csrf_exempt
@allow_methods(['POST'])
@transaction.atomic
def register(request):
    """
    Register a user. Takes input:

    email: string
    password: string
    username: string

    Return json data either
        {'success': True, 'user': {'id': ...}}
    or
        {'error': <error message>}

    Pick the way of implementation you feel most comfortable with. However,
    a robustness implementation should at least do the following things
    1. Check if the email exists. If exists, return message to client saying that the email is occupied
    2. Check if the lengths or email, username, password match the requirement of database (i.e, not too long)
    3. Create a user through the User class. The user.role should be User.ROLE_AUTHOR
    4. Return data as indicated above
    """
    email = request.REQUEST.get('email', None)
    username = request.REQUEST.get('username', None)
    password = request.REQUEST.get('password', None)

    if not email or not username or not password:
        return HttpResponseBadRequest()

    existed_user = User.objects.filter(email=email)
    if existed_user.exists():
        return HttpResponse(json.dumps({'error': 'duplicate email'}))

    password = md5(password)
    new_user = User(email=email, username=username, password=password, role=User.ROLE_AUTHOR)
    new_user.save()

    return HttpResponse(json.dumps({'success': True}))


@csrf_exempt
@json_view
@allow_methods(['POST'])
@login_required_otherwise_401
def update_profile(request):
    user = User.objects.get(id=request.session.get('user')['id'])
    data = request.REQUEST

    if 'username' in data:
        if not data['username']:
            return {'error': 'username can not be empty'}

        user.username = data['username']

    if 'description' in data:
        user.description = data['description']

    if data.get('original_password', '') and data.get('new_password', ''):
        hashed_password = md5(data['original_password'])
        if user.password != hashed_password:
            return {'error': 'password incorrect'}
        else:
            user.password = md5(data['new_password'])

    if 'avatar' in request.FILES:
        fs = request.FILES['avatar']
        filename = fs.name
        print filename
        filecontent = fs.read()

        img_dir = os.path.join(MEDIA_ROOT, 'image')
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)

        uid = str(uuid.uuid1()).replace('-', '')
        savepath = os.path.join(img_dir, uid + os.path.splitext(filename)[1])

        out_fs = open(savepath, 'wb')
        out_fs.write(filecontent)
        out_fs.close()

        user.avatar = savepath.replace(BASE_DIR, '')

    user.save()
    write_user_info_to_session(user, request)
    return {'success': True}


@csrf_exempt
@transaction.atomic
@json_view
@allow_methods(['POST'])
def reset_password(request):
    data = request.REQUEST
    if 'email' not in data:
        return HttpResponseBadRequest('email not provided')

    email = data['email']
    user = User.objects.filter(email=email, deleted=0)
    if not user.exists():
        return {'error': 'email invalid'}

    user = user[0]
    newpassword = str(uuid.uuid1()).replace('-', '')
    user.password = md5(newpassword)
    user.save()

    send_mail('Reset Password', user.username + ': Your password has been reset to: '
              + newpassword + '. Please use this to log on the modify your password',
              from_email=EMAIL_HOST_USER, recipient_list=[email])

    return {'success': True}

############
# Articles #
############

def get_articles(request):
    """
    :param request: contains the following parameters
        query   : a search string. If provided, any document doesn't contain the string in the title should
                  be excluded
        sort    : a string. Valid values are: '[+/-]time' - sort by time ascending or descending; '[+/-title]' sort by
                  title alphabetically ascending or descending. If not provided, default is '-time'
        page    : a number. 0, 1, 2, ... (start from zero), default is 0
        count   : how many articles to return at most for this page. If not provided, default is 10
    :return: json array, each element is {"title": ..., "content": ..., "time": string in format of "%Y-%m-%d %H:%M:%D",
             "author": {"username": ..., "id": ...} }
    Only support GET method
    """

    # Do integrity check
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    query = request.GET.get('query', None)
    sort  = request.GET.get('sort', '-time')
    # print request.GET
    if sort not in ('-time', '+time', '-title', '+title'):
        return HttpResponseBadRequest('Invalid sort option')
    if sort[1:] == 'time':
        sort += '_create'  # Turn to +/- time_create
    if sort[0] == '+':
        sort = sort[1: ]

    page = request.GET.get('page', '0')
    if not page.isdigit():
        return HttpResponseBadRequest('Invalid page num')

    count = request.GET.get('count', '10')
    if not count.isdigit():
        return HttpResponseBadRequest('Invalid record count')

    # print query, sort, page, count

    # Start searching
    total_count, result = Article.objects.search(query=query, sort=sort, page=int(page), count=int(count), published=True)
    response_data = [{'id': article.id, 'title': article.title, 'content': article.content,
                      'time': article.time_create.strftime('%Y-%m-%d %H:%M:%S'),
                      'author': {'id': article.author.id, 'username': article.author.username}} for article in result]

    return HttpResponse(json.dumps(response_data))


@csrf_exempt
@login_required_otherwise_401
@transaction.atomic
def create_article(request):
    """
    request parameters:
    title: string
    content: string
    state: string, either 'published' or 'draft'
    :return: json, in form of {'success': True, 'article': {'id': ...}} or {'error': <error message>}
    """
    user = request.session.get('user')
    title = request.REQUEST['title']
    content = request.REQUEST['content']
    state = request.REQUEST['state']

    if state not in ('published', 'draft'):
        return HttpResponseBadRequest('invalid state')

    if state == 'published':
        state = Article.STATE_PUBLISHED
    else:
        state = Article.STATE_UNPUBLISHED

    article = Article.objects.create(author_id=user['id'], title=title,
                                     content=content, state=state, time_create=datetime.now(),
                                     time_update=datetime.now())

    return HttpResponse(json.dumps({'article': {'id': article.id}}))





@csrf_exempt
@transaction.atomic
@article_operation(author_required=True)
@allow_methods(['POST'])
def update_article(request, article_id):
    """
    :param request: contains the updated fields. Refer to the create_article controller for fields contained
    :param article_id: id of the target article
    :return: json, {"success": True} or {"error": <error message>}
    """
    article = Article.objects.get(id=int(article_id))
    data = request.REQUEST
    if 'title' in data:
        article.title = data['title']
        print article.title, article_id

    if 'content' in data:
        article.content = data['content']

    if 'state' in data:
        if data['state'] not in ('published', 'draft'):
            return HttpResponseBadRequest('invalid state')
        if data['state'] == 'published':
            article.state = Article.STATE_PUBLISHED
        else:
            article.state = Article.STATE_UNPUBLISHED

    article.time_update = datetime.now()
    article.save()

    article = Article.objects.get(id=int(article_id))

    return HttpResponse(json.dumps({'success': True, 'article': {'id': article.id}}))


@csrf_exempt
@allow_methods(['POST'])
@article_operation(author_required=True)
@transaction.atomic
def delete_article(request, article_id):
    article = Article.objects.get(id=article_id)
    article.deleted = 1
    article.save()
    return HttpResponse(json.dumps({'success': True}))




###############
# Follow APIs #
###############

@csrf_exempt
@login_required_otherwise_401
@allow_methods(['POST'])
def follow(request):
    data = request.REQUEST
    if 'target_user_id' not in data:
        return HttpResponseBadRequest('target_user_id must be provided')

    if int(data['target_user_id']) == request.session.get('user')['id']:
        return HttpResponseBadRequest('Cannot do this to oneself')

    target_user = User.objects.find_by_id(int(data['target_user_id']))
    if target_user is None:
        return HttpResponseNotFound('target user not found')

    user = User.objects.find_by_id(request.session.get('user')['id'])
    user.add_following(target_user)

    return HttpResponse(json.dumps({'success': True}))


@csrf_exempt
@login_required_otherwise_401
@allow_methods(['POST'])
def unfollow(request):
    data = request.REQUEST
    if 'target_user_id' not in data:
        return HttpResponseBadRequest('target_user_id must be provided')

    if int(data['target_user_id']) == request.session.get('user')['id']:
        return HttpResponseBadRequest('Cannot do this to oneself')

    target_user = User.objects.find_by_id(int(data['target_user_id']))
    if target_user is None:
        return HttpResponseNotFound('target user not found')

    user = User.objects.find_by_id(request.session.get('user')['id'])
    user.remove_following(target_user)

    return HttpResponse(json.dumps({'success': True}))

@login_required_otherwise_401
@allow_methods(['GET'])
def get_followers(request):
    user_id = request.REQUEST.get('user_id', None)
    if user_id is None:
        user_id = request.session.get('user')['id']
    else:
        user_id = int(user_id)

    user = User.objects.find_by_id(user_id)

    followers = user.get_followers()

    return HttpResponse(json.dumps([{'id': u.id, 'username': u.username} for u in followers]))

@allow_methods(['GET'])
@login_required_otherwise_401
def get_followings(request):
    user_id = request.REQUEST.get('user_id', None)
    if user_id is None:
        user_id = request.session.get('user')['id']
    else:
        user_id = int(user_id)

    user = User.objects.find_by_id(user_id)

    followings = user.get_followings()

    return HttpResponse(json.dumps([{'id': u.id, 'username': u.username} for u in followings]))

#############
# User Like #
#############

@csrf_exempt
@json_view
@login_required_otherwise_401
@allow_methods(['POST'])
@article_operation(False)
def article_set_like(request, article_id):
    article = Article.objects.get(id=article_id)
    user = get_logon_user(request)

    data = request.REQUEST
    to_like = data.get('like', None)
    if to_like is None:
        return HttpResponseBadRequest('parameter missing')

    to_like = int(to_like)
    if to_like == 1:
        article.add_like_user(user)
    else:
        article.remove_like_user(user)

    return {'success': True, 'like_num': article.like_num}

@csrf_exempt
@json_view
@login_required_otherwise_401
@allow_methods(['POST'])
@article_operation(False)
def add_comment(request, article_id):
    article = Article.objects.get(id=article_id)
    user = get_logon_user(request)

    content = request.REQUEST.get('content', '')
    if not content:
        return {'error': 'content can not be empty'}

    comment = ArticleComment.objects.create(user_id=user.id, article_id=article.id, content=content, time=datetime.now())
    return {'user': {'id': user.id, 'username': user.username, 'avatar': user.avatar},
            'id': comment.id,
            'time': comment.time,
            'content': comment.content}

@csrf_exempt
@json_view
@login_required_otherwise_401
@allow_methods(['POST'])
def delete_comment(request, comment_id):
    comment = ArticleComment.objects.filter(id=comment_id)
    if not comment.exists():
        return HttpResponseNotFound()
    comment = comment[0]
    
    user = get_logon_user(request)
    if not user.id == comment.user_id:
        return HttpResponseForbidden()

    comment.delete()
    return {'success': True}


