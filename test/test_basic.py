from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS, DEFAULT_USER_NAME
import unittest
from util import proxy, md5, BaseTestCase
from pyquery import PyQuery
from load_data import load_data
from datetime import datetime
import requests, json

class BasicTestCase(BaseTestCase):

	def setUp(self):
		data = load_data()
		for item in data:
			item['time'] = datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S')
		self.data = sorted(data, key=lambda i: i['time'], reverse=True)

	def find_titles(self, html):
		doc = PyQuery(html)

		article_elems = doc('.article-list-item-main')

		titles = sorted([elem.get('data-article-title') for elem in article_elems])
		return titles

	def test_index(self):
		res = proxy(WEBSITE_ADDRESS)
		titles = self.find_titles(res)
		groundtruth = sorted([item['title'] for item in self.data][: len(titles)])

		self.assertTrue(titles == groundtruth)

	def test_homepage(self):
		# Log in first
		session = self.login()

		# Request homepage
		res = session.get('%s/homepage' %WEBSITE_ADDRESS)
		titles = self.find_titles(res.text)

		groundtruth = sorted([item['title'] for item in self.data if item['author'] is None][: len(titles)])
		self.assertEqual(titles, groundtruth)




if __name__ == '__main__':
	unittest.main()

		

