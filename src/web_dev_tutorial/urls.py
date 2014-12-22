from django.conf.urls import patterns, include, url
from django.contrib import admin
from app.controllers import api, practise, webpages

urlpatterns = patterns('',
    # Web page list

    url(r'^$', webpages.all_articles),
    url(r'^articles$', webpages.all_articles),
    url(r'^article$', webpages.article_detail),
    url(r'^feeds$', webpages.feeds),

    url(r'^create_article$', webpages.create_article),

    url(r'^people$', webpages.people),
    url(r'^homepage$', webpages.user_homepage),

    url(r'^login$', webpages.login),
    url(r'^logout$', webpages.logout),
    url(r'^register$', webpages.register),

    url(r'^about$', webpages.about),

    # API list
    url(r'^api/login$', api.login),
    url(r'^api/article/list$', api.get_articles),
    url(r'^api/article/create$', api.create_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/update$', api.update_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/set_state$', api.update_article),
    url(r'^api/article/(?P<article_id>[0-9]+)/delete$', api.delete_article),

    # Practise
    url(r'^practise/heartbeat$', practise.heart_beat),
    # TODO: Define your url dispatcher for the rest of controllers!
    url(r'^practise/file/create', practise.create_file),
    url(r'^practise/file/(?P<file_id>[0-9a-zA-z]+)/get', practise.get_file),
)
