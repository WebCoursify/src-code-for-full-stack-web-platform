from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from app.models import *
import json

def login(request):
    email = request.REQUEST.get('email', None)
    password = request.REQUEST.get('password', None)

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
        query   : a search string. If provided, any document doesn't contain the string in either title or content should
                  be excluded
        sort    : a string. Valid values are: '[+/-]time' - sort by time ascending or descending; '[+/-title]' sort by
                  title alphabetically ascending or descending
        offset  : a number. If provided, skip the first <offset> documents
        limit   : Return how many articles at most. If not provided, default is 10
    :return: json array, each element is {"title": ..., "content": ..., "time": string in format of "%Y-%m-%d %H:%M:%D",
             "author": {"username": ..., "id": ...} }
    """
    # TODO: Implement this
    return None


def create_article(request):
    # TODO
    pass


def update_article(request, article_id):
    """
    :param request: contains the updated content
    :param article_id: id of the target article
    :return: json, {"success": True} or {"error": <error message>}
    """
    # TODO: Implement me
    return None








