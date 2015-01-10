from django.conf.urls import patterns, include, url
from django.contrib import admin
from app.controllers import api, practise, webpages
from web_dev_tutorial import settings

urlpatterns = patterns('',
    # Web page list

    url(r'^$', webpages.all_articles),
    url(r'^articles$', webpages.all_articles),
    url(r'^article$', webpages.article_detail),
    url(r'^feeds$', webpages.feeds),

    url(r'^create_article$', webpages.create_article),
    url(r'^edit_article$', webpages.edit_article),

    url(r'^people$', webpages.people),
    url(r'^homepage$', webpages.user_homepage),

    url(r'^profile/edit$', webpages.profile_edit),
    url(r'^profile/change_password$', webpages.profile_change_password),
    url(r'^profile/avatar$', webpages.profile_avatar),

    url(r'^login$', webpages.login),
    url(r'^logout$', webpages.logout),
    url(r'^register$', webpages.register),
    url(r'^reset_password$', webpages.reset_password),

    url(r'^about$', webpages.about),

    # API list
    url(r'^api/login$', api.login),
    url(r'^api/register$', api.register),
    url(r'^api/profile/update$', api.update_profile),
    url(r'^api/password/update$', api.update_profile),
    url(r'^api/avatar/update$', api.update_profile),
    url(r'^api/reset_password$', api.reset_password),

    url(r'^api/article/list$', api.get_articles),
    url(r'^api/article/create$', api.create_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/update$', api.update_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/set_state$', api.update_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/delete$', api.delete_article),

    url(r'^api/article/(?P<article_id>[0-9]+)/set_like$', api.article_set_like),

    url(r'^api/user/follow$', api.follow),
    url(r'^api/user/unfollow$', api.unfollow),
    url(r'^api/user/followers', api.get_followers),
    url(r'^api/user/followings', api.get_followings),

    # Practise
    url(r'^practise/heartbeat$', practise.heart_beat),
    # TODO: Define your url dispatcher for the rest of controllers!
    url(r'^practise/file/create', practise.create_file),
    url(r'^practise/file/(?P<file_id>[0-9a-zA-z]+)/get', practise.get_file),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^upload/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))