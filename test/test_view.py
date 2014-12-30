from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS, DEFAULT_USER_NAME, \
                   ARTICLE_TABLE_NAME, USER_TABLE_NAME
import unittest
from util import proxy, BaseTestCase
import random
import uuid
import json
import time
from datetime import datetime
from monsql import DESCENDING

from test_model import ModelBaseTestCase
from pyquery import PyQuery

def test_case(title):
    def decorator(func):
        def inner(*args, **kwargs):
            print "===========Testing: %s===========" %title
            return func(*args, **kwargs)
        return inner
    return decorator

class ViewBaseTestCase(ModelBaseTestCase):
    pass

class IndexViewTestCase(ViewBaseTestCase):

    @test_case('(1) Home Page')
    def test_search(self):
        search_url = WEBSITE_ADDRESS + '/articles'

        test_cases = [
            # Each test case is (query, page, count)
            (None, None, None),
            ('a', None, None),
            (None, 1, None),
            (None, None, 100),
        ]

        article_table = self.db.get(ARTICLE_TABLE_NAME)

        for query, page, count in test_cases:
            # The returned result
            html = proxy(search_url, 'get', {'query': query, 'page': page, 'count': count})
            doc = PyQuery(html)
            article_elems = doc('.article-list-item-main')
            titles = [elem.get('data-article-title') for elem in article_elems]

            # The groundtruth
            if page is None: page = 0
            if count is None: count = 10

            filter = {'state': 2, 'deleted': 0}
            if query:
                filter['title'] = {'$contains': query}

            articles = article_table.find(filter=filter, sort=[('time_create', DESCENDING)], skip=page * count, limit=count)
            real_titles = [item.title for item in articles]

            self.assertEqual(titles, real_titles, 'Article index test fails at the case of (%s,%s,%s)' \
                             %(query, page, count))


class EditArticleTestCase(ViewBaseTestCase):

    @test_case('(2) Edit Article')
    def test_edit_article_page(self):
        # default user
        user_id = self.find_default_user_id()
        session = self.login()

        article_table = self.db.get(ARTICLE_TABLE_NAME)
        articles = article_table.find({'author_id': user_id, 'deleted': 0})

        other_peoples_articles = article_table.find({'$not': {'author_id': user_id}, 'deleted': 0})

        print "It should display original title"
        for idx, article in enumerate(articles[: 10]):
            response = session.get(WEBSITE_ADDRESS + '/edit_article?id=%d' %(article.id))

            doc = PyQuery(response.text)
            title_input = doc('input[name="title"]')
            self.assertTrue(len(title_input) > 0)
            title_input = title_input[0]

            self.assertEqual(title_input.get('value'), article.title)

        print "It should only allow author to visit"
        for idx, article in enumerate(other_peoples_articles[: 10]):
            response = session.get(WEBSITE_ADDRESS + '/edit_article?id=%d' %(article.id))
            self.assertEqual(response.status_code, 404)

class ArticlePageTestCase(ViewBaseTestCase):

    @test_case('(3) Article Page')
    def test_article_page(self):
        # default user
        user_id = self.find_default_user_id()
        session = self.login()

        article_table = self.db.get(ARTICLE_TABLE_NAME)
        articles = article_table.find({'author_id': user_id, 'deleted': 0})
        other_peoples_articles = article_table.find({'$not': {'author_id': user_id}, 'deleted': 0})

        print "It should display the three button for one's own articles "
        for idx, article in enumerate(articles[: 10]):
            # print idx
            response = session.get(WEBSITE_ADDRESS + '/article?id=%d' %(article.id))

            doc = PyQuery(response.text)
            self.assertGreater(len(doc('.btn-edit-article')), 0)
            self.assertGreater(len(doc('.btn-delete-article')), 0)
            self.assertGreater(len(doc('.btn-change-article-state')), 0)

        print "It shouldn't display the buttons to non-authors"
        for idx, article in enumerate(other_peoples_articles[: 10]):
            response = session.get(WEBSITE_ADDRESS + '/article?id=%d' %(article.id))

            doc = PyQuery(response.text)
            self.assertEqual(len(doc('.btn-edit-article')), 0)
            self.assertEqual(len(doc('.btn-delete-article')), 0)
            self.assertEqual(len(doc('.btn-change-article-state')), 0)

        print "We didn't test the behaviors of these buttons. You'll need to test them"

if __name__ == '__main__':
    unittest.main()


