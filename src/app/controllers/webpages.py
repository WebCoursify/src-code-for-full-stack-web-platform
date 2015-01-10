from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response, redirect
from app.models import *
import math
from django.db.models import Q


def login_required(controller):
    def inner(request):
        if 'user' not in request.session:
            return redirect('/login')
        return controller(request)

    return inner


def response404():
    response = render_to_response('./404.html', locals())
    response.status_code = 404
    return response

def get_pager_data(page, count, total_page_count):
    curr_page = int(page)
    prev_page = curr_page - 1
    next_page = curr_page + 1
    last_page = (total_page_count + count - 1) / count - 1
    if last_page < 0:
        last_page = 0
    page_range = [i for i in range(curr_page - 3, curr_page + 3) if i >= 0 and i <= last_page]
    return curr_page, prev_page, next_page, last_page, page_range

###################################
# Main pages, related to articles #
###################################


def all_articles(request):
    """
    This naive implementation only return the 10 most recent public articles
    A correct implementation should support query, page, count parameters as in api.get_articles
    """

    query = request.GET.get('query', None)
    page = request.GET.get('page', '0')
    count = request.GET.get('count', '10')

    if page:
        page = int(page)
    else:
        page = None

    if count:
        count = int(count)
    else:
        count = None

    total_count, articles = Article.objects.search(query=query, sort='-time_create', page=int(page), count=int(count), published=True)

    nav = 'all'  # For correct tab display on the front end, please leave this untouched

    curr_page, prev_page, next_page, last_page, page_range = get_pager_data(page, count, total_count)
    return render_to_response('./index.html', locals())

def feeds(request):
    """
    This controller returns articles of the authors followed by the log on user
    Need to support the same parameters as all_articles
    """
    nav = 'feeds'  # For correct tab display on the front end, please leave this untouched
    return render_to_response('./index.html', locals())


def people(request):
    """
    This naive implementation only return 10 users sorted by id
    Should support query parameters:
    query   : exclude users who don't contain the query in their name or description
    page    : as usual
    count   : as usual
    """
    query = request.REQUEST.get('query', None)
    page = request.REQUEST.get('page', 0)
    count = request.REQUEST.get('count', 10)

    if page == '':
        page = 0
    if count == '':
        count = 10

    page = int(page)
    count = int(count)

    users = User.objects.filter(deleted=0)
    if query:
        users = users.filter(Q(username__contains=query) | Q(description__contains=query))

    total_count = len(users)
    users = users[count * page: (page + 1) * count]

    # The following code put retrieved users in two-item group, so it's easier to render two users
    # each row in the front end
    chunk_size = 2
    user_chunks = [users[i * chunk_size: (i + 1) * chunk_size] for i in
                   range(int(math.ceil(len(users) / float(chunk_size))))]

    curr_page, prev_page, next_page, last_page, page_range = get_pager_data(page, count, total_count)
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
    5. The most recent articles(5 at most) of this author, with this article excluded

    If the user is log on and is the author is the article, the button
    to publish/unpublish this article, the button to enter edit page,
    the button to delete this article should be rendered. Otherwise not rendered.
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
    """
    return render_to_response('./create_article.html', locals())

@login_required
def edit_article(request):
    """
    Render the page for editing an article
    Should require the log on user be the author of this article
    """
    article_id = request.GET.get('id', None)
    if not article_id:
        return response404()
    article = Article.objects.filter(id=int(article_id), deleted=0)
    if not article.exists():
        return response404()

    article = article[0]
    user = request.session.get('user')
    if article.author_id != user['id']:
        return response404()

    return render_to_response('./create_article.html', locals())


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


def reset_password(request):
    return render_to_response('./reset_password.html', locals())

@login_required
def profile_edit(request):
    user = User.objects.get(id=request.session.get('user')['id'])
    nav = 'edit'
    return render_to_response('./user_profile_edit.html', locals())


@login_required
def profile_change_password(request):
    user = User.objects.get(id=request.session.get('user')['id'])
    nav = 'password'
    return render_to_response('./user_profile_password.html', locals())


@login_required
def profile_avatar(request):
    user = User.objects.get(id=request.session.get('user')['id'])
    nav = 'avatar'
    return render_to_response('./user_profile_avatar.html', locals())


################
# Other stuffs #
################


def about(request):
    return render_to_response('./about.html', locals())