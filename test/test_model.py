from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS, DEFAULT_USER_NAME, \
                   ARTICLE_TABLE_NAME, USER_TABLE_NAME
import unittest
from monsql import MonSQL, ASCENDING, DESCENDING
from util import proxy, BaseTestCase
import random
import uuid
import json
import MySQLdb
import time

def random_string():
    return str(uuid.uuid1())

class ModelBaseTestCase(BaseTestCase):
    def setUp(self):
        self.db = MonSQL(MYSQL_HOST, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB_NAME)
        self.db.commit()

    def tearDown(self):
        self.db.close()

class SearchTestCase(ModelBaseTestCase):

    def test_search(self):
        search_url = WEBSITE_ADDRESS + '/api/article/list'

        test_cases = [
            # Each test case is (query, sort, page, count)
            (None, None, None, None),
            ('a', None, None, None),
            (None, '+time', None, None),
            (None, None, 1, None),
            (None, None, None, 100),
        ]

        article_table = self.db.get(ARTICLE_TABLE_NAME)

        for query, sort, page, count in test_cases:
            # The returned result
            res = json.loads(proxy(search_url, 'get', {'query': query, 'sort': sort, 'page': page, 'count': count}))
            response_ids = [item['id'] for item in res]

            # The groundtruth
            if page is None: page = 0
            if count is None: count = 10
            if sort is None: sort = '-time'

            filter = {'state': 2}
            if query:
                filter['title'] = {'$contains': query}

            sort_tag, sort_field = sort[0], sort[1: ]
            if sort_field == 'time':
                sort_field = 'time_create'

            if sort_tag == '+': 
                sorting = (sort_field, ASCENDING)
            elif sort_tag == '-': 
                sorting = (sort_field, DESCENDING)

            articles = article_table.find(filter=filter, sort=[sorting], skip=page * count, limit=count)
            real_ids = [item.id for item in articles]
            # print response_ids
            # print real_ids

            self.assertEqual(response_ids, real_ids, 'Article search test fails at the case of (%s,%s,%s,%s)' \
                             %(query, sort, page, count))



class ArticleTestCase(ModelBaseTestCase):

    def test_update(self):
        def get_update_url(article_id):
            return WEBSITE_ADDRESS + '/api/article/%d/update' %(article_id)
        def get_set_state_url(article_id):
            return WEBSITE_ADDRESS + '/api/article/%d/set_state' %(article_id)

        session = self.login()
        user = self.db.get(USER_TABLE_NAME).find_one({'email': DEFAULT_USER_NAME + '@gmail.com'})

        article_table = self.db.get(ARTICLE_TABLE_NAME)
        articles = article_table.find({'author_id': user.id, 'deleted': 0})[: 10]

        for article in articles:

            self.assertTrue(article.state in (1, 2))
            update_url = get_update_url(article.id)

            random_title, random_content = random_string(), random_string()

            # Change the state
            if article.state == 1:
                new_state = 'published'
            elif article.state == 2:
                new_state = 'draft'

            response = session.post(update_url, data={'title': random_title, 'content': random_content, 'state': new_state})
            self.assertTrue(response.json().get('success', None))

            article_table.commit() # This is important because otherwise it won't see the newest result
            updated_article = article_table.find_one({'id': article.id})

            self.assertEqual(updated_article.title, random_title)
            self.assertEqual(updated_article.content, random_content)
            if new_state == 'published':
                self.assertEqual(updated_article.state, 2)
            else:
                self.assertEqual(updated_article.state, 1)

            # Test changing state
            for i in range(2):
                article_table.commit()
                current_article = article_table.find_one({'id': article.id})

                if current_article.state == 1:
                    new_state = 'published'
                elif current_article.state == 2:
                    new_state = 'draft'

                response = session.post(get_set_state_url(current_article.id), data={'state': new_state})
                self.assertTrue(response.json().get('success', None))

                article_table.commit()
                updated_article = article_table.find_one({'id': article.id})

                if current_article.state == 1:
                    self.assertEqual(updated_article.state, 2)
                elif current_article.state == 2:
                    self.assertEqual(updated_article.state, 1)

            # Cancel any change
            article_table.update({'id': article.id}, 
                                 {'title': article.title, 'content': article.content, 'state': article.state})
            article_table.commit()

    def test_delete(self):
        def get_delete_url(article_id):
            return WEBSITE_ADDRESS + '/api/article/%d/delete' %(article_id)

        session = self.login()
        user = self.db.get(USER_TABLE_NAME).find_one({'email': DEFAULT_USER_NAME + '@gmail.com'})

        article_table = self.db.get(ARTICLE_TABLE_NAME)
        articles = article_table.find({'author_id': user.id, 'deleted': 0}, limit=10)

        for article in articles:
            # Before delete, make sure we can visit this article
            response = session.get(WEBSITE_ADDRESS + '/article?id=' + str(article.id))
            self.assertEqual(response.status_code, 200)

            # Delete it
            response = session.post(get_delete_url(article.id))
            # print response.text
            self.assertTrue(response.json().get('success', None))

            # Now visit again will be 404
            response = session.get(WEBSITE_ADDRESS + '/article?id=' + str(article.id))
            self.assertEqual(response.status_code, 404)
            

class FollowRelationTestCase(ModelBaseTestCase):

    def set_follow(self, session, target_user_id):
        response = session.post(WEBSITE_ADDRESS + '/api/user/follow', data={'target_user_id': target_user_id})
        self.assertTrue(response.json().get('success', None))

    def get_follower_list(self, session, user_id=None):
        data = {}
        if user_id is not None:
            data['user_id'] = user_id

        response = session.get(WEBSITE_ADDRESS + '/api/user/followers', data={})
        return response.json()

    def set_unfollow(self, session, target_user_id):
        response = session.post(WEBSITE_ADDRESS + '/api/user/unfollow', data={'target_user_id': target_user_id})
        self.assertTrue(response.json().get('success', None))

    def test_follow(self):
        users = self.db.get(USER_TABLE_NAME).find({'deleted': 0}, limit=20)

        user_group_a = users[: 10]
        user_group_b = users[10: 20]

        for user_a in user_group_a:
            session = self.login(user_a.email, user_a.password)
            
            for user_b in user_group_b:

                self.set_follow(session, user_b)

            self.assertEqual(sorted([u['id'] for u in self.get_follower_list(session)]), 
                             sorted([u.id for u in user_b]))

        session = self.login() # Default user
        for user_a in user_group_a:
            self.assertEqual(sorted([u['id'] for u in self.get_follower_list(session, target_user_id=user_a.id)]), 
                             sorted([u.id for u in user_b]))


        # Test unfollow
        for user_a in user_group_a:
            session = self.login(user_a.email, user_a.password)
            
            for user_b in user_group_b:
                self.set_unfollow(session, user_b)

            self.assertEqual(self.get_follower_list(session), [])

    def test_follow_throughput(self):
        # TODO:
        pass


if __name__ == '__main__':
    unittest.main()


