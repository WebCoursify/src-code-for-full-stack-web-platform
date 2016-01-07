from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from datetime import datetime
from app.models import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import hashlib
from controller_common import get_argument

def md5(stream):
    m = hashlib.md5()
    m.update(stream)
    return m.hexdigest()

def login_required_otherwise_401(controller):
    def inner(request):
        if 'user' not in request.session:
            return HttpResponse('Unauthorized', status=401)
        else:
            return controller(request)
    return inner

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
    # TODO: Implement this
    return None


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


def update_article(request, article_id):
    """
    :param request: contains the updated fields. Refer to the create_article controller for fields contained
    :param article_id: id of the target article
    :return: json, {"success": True} or {"error": <error message>}
    """
    # TODO: Implement me
    return HttpResponse(article_id)








