from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from datetime import datetime
from app.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import hashlib
from controller_common import get_argument


##############
# Decorators #
##############

def md5(stream):
    m = hashlib.md5()
    m.update(stream)
    return m.hexdigest()

##############
# Decorators #
##############

def login_required_otherwise_401(controller):
    def inner(request):
        if 'user' not in request.session:
            return HttpResponse('Unauthorized', status=401)
        else:
            user_id = request.session.get('user')['id']
            user = User.objects.find_by_id(user_id)
            if user is None:
                return HttpResponse('Invalid user', status=403)
            return controller(request)
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

        if getattr(controller, 'csrf_exempt', False):
            inner.csrf_exempt = True

        return inner

    return decorator



def login(request):
    email = get_argument(request, 'email', None)
    password = get_argument(request, 'password', None)
    if email is None or password is None:
        return HttpResponseBadRequest('email and password required')

    password = md5(password)
    user = User.objects.filter(email=email, password=password, deleted=0)
    if not user.exists():
        return HttpResponse(json.dumps({'error': 'Incorrect email/password'}))

    user = user[0]
    request.session['user'] = {'id': user.id, 'username': user.username}

    return HttpResponse(json.dumps({'success': True}))


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
    # TODO: Implement this
    return None


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
    title = get_argument(request, 'title')
    content = get_argument(request, 'content')
    state = get_argument(request, 'state')

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


<<<<<<< 9bb5269a3452e685c5dd972abc23371553492f8f
<<<<<<< 1719af997da69b934c2d476b2a0e776efb290812

=======
def article_operation(author_required=False):
    def decorator(controller):

        def inner(*args, **kwargs):
            request, article_id = args[0], kwargs['article_id']
            print article_id

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

        if getattr(controller, 'csrf_exempt', False):
            inner.csrf_exempt = True

        return inner

    return decorator
>>>>>>> finish model-article
=======

>>>>>>> finish follow relation


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
    
    title = get_argument(request, 'title')
    content = get_argument(request, 'content')
    state = get_argument(request, 'state')

    if title is not None:
        article.title = title

    if content is not None:
        article.content = content

    if state is not None:
        if state not in ('published', 'draft'):
            return HttpResponseBadRequest('invalid state')
        if state == 'published':
            article.state = Article.STATE_PUBLISHED
        else:
            article.state = Article.STATE_UNPUBLISHED

    article.time_update = datetime.now()
    article.save()

    article = Article.objects.get(id=int(article_id))

    return HttpResponse(json.dumps({'success': True, 'article': {'id': article.id}}))


<<<<<<< 9bb5269a3452e685c5dd972abc23371553492f8f
<<<<<<< 1719af997da69b934c2d476b2a0e776efb290812
@csrf_exempt
@allow_methods(['POST'])
@article_operation(author_required=True)
=======
@allow_methods(['POST'])
@article_operation(author_required=True)
@csrf_exempt
>>>>>>> finish model-article
=======
@csrf_exempt
@allow_methods(['POST'])
@article_operation(author_required=True)
>>>>>>> finish follow relation
@transaction.atomic
def delete_article(request, article_id):
    article = Article.objects.get(id=article_id)
    article.deleted = 1
    article.save()
    return HttpResponse(json.dumps({'success': True}))


<<<<<<< 1719af997da69b934c2d476b2a0e776efb290812


###############
# Follow APIs #
###############

@csrf_exempt
@login_required_otherwise_401
@allow_methods(['POST'])
def follow(request):
    target_user_id = get_argument(request, 'target_user_id')
    if target_user_id is None:
        return HttpResponseBadRequest('target_user_id must be provided')

    if int(target_user_id) == request.session.get('user')['id']:
        return HttpResponseBadRequest('Cannot do this to oneself')

    target_user = User.objects.find_by_id(int(target_user_id))
    if target_user is None:
        return HttpResponseNotFound('target user not found')

    user = User.objects.find_by_id(request.session.get('user')['id'])
    user.add_following(target_user)

    return HttpResponse(json.dumps({'success': True}))


@csrf_exempt
@login_required_otherwise_401
@allow_methods(['POST'])
def unfollow(request):
    target_user_id = get_argument(request, 'target_user_id')
    if target_user_id is None:
        return HttpResponseBadRequest('target_user_id must be provided')

    if int(target_user_id) == request.session.get('user')['id']:
        return HttpResponseBadRequest('Cannot do this to oneself')

    target_user = User.objects.find_by_id(int(target_user_id))
    if target_user is None:
        return HttpResponseNotFound('target user not found')

    user = User.objects.find_by_id(request.session.get('user')['id'])
    user.remove_following(target_user)

    return HttpResponse(json.dumps({'success': True}))

@login_required_otherwise_401
@allow_methods(['GET'])
def get_followers(request):
    user_id = get_argument(request, 'user_id')
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
    user_id = get_argument(request, 'user_id')
    if user_id is None:
        user_id = request.session.get('user')['id']
    else:
        user_id = int(user_id)

    user = User.objects.find_by_id(user_id)

    followings = user.get_followings()

    return HttpResponse(json.dumps([{'id': u.id, 'username': u.username} for u in followings]))
=======
>>>>>>> finish model-article


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








