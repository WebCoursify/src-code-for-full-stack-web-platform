from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from app.models import *
import math


def login_required(controller):
    def inner(request):
        if 'user' not in request.session:
            return redirect('/login')
        return controller(request)

    return inner

def response404():
    return redirect('/404')

###################################
# Main pages, related to articles #
###################################


def all_articles(request):
    articles = Article.objects.filter(deleted=0, state=Article.STATE_PUBLISHED).order_by('-time_create')[: 10]
    nav = 'all'
    return render_to_response('./index.html', locals())


def feeds(request):
    nav = 'feeds'
    return render_to_response('./index.html', locals())


def people(request):
    users = User.objects.filter(deleted=0)[: 10]

    chunk_size = 2
    user_chunks = [users[i * chunk_size: (i + 1) * chunk_size] for i in range(int(math.ceil(len(users) / float(chunk_size))))]

    return render_to_response('./people.html', locals())


def user_homepage(request):
    uid = request.REQUEST.get('id', None)
    if uid is None:
        if 'user' in request.session:
            user = User.objects.filter(deleted=0, id=request.session.get('user')['id'])
        else:
            return response404()
    else:
        user = User.objects.filter(id=int(uid), deleted=0)

    if not user.exists():
        return response404()

    user = user[0]
    articles = Article.objects.filter(author_id=user.id)
    if 'user' not in request.session or request.session.get('user')['id'] != user.id:
        articles = articles.filter(state=Article.STATE_PUBLISHED)

    articles = articles.order_by('-time_create')[: 10]

    return render_to_response('./user_homepage.html', locals())


def article_detail(request):
    """
    :param: request.GET['id']
    Render the page of a single article. It should contains:
    1. The full information of this article
    2. The author's information
    3. All comments
    4. All likes
    If the user is log on and is the author is the article, the button
    to publish/unpublish this article, the button to enter edit page,
    the button to delete this article should be rendered
    """
    article_id = request.GET.get('id', None)
    if article_id is None:
        return response404()

    article = Article.objects.filter(id=article_id, deleted=0)
    if not article.exists():
        return response404()

    article = article[0]

    # TODO: Add more implementations

    return render_to_response('./article.html', locals())

@login_required
def create_article(request):
    """
    Render the page for creating an article
    Should required log on user
    """
    return render_to_response('./create_article.html', locals())


def edit_article(request):
    """
    Render the page for editing an article
    Should require the log on user be the author of this article
    """
    # TODO: Implement this
    return None


def user_liked_articles(request):
    """
    Render a page with articles the log on user liked
    Should consider re-using the template of user homepage
    """
    # TODO: Implement this
    return None

########################
# User management zone #
########################


def login(request):
    return render_to_response('./login.html', locals())


def register(request):
    return render_to_response('./register.html', locals())


def logout(request):
    if 'user' in request.session:
        del request.session['user']
    return redirect('/')


def about(request):
    return render_to_response('./about.html', locals())