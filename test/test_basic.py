from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS
import unittest
from util import proxy
from pyquery import PyQuery
from load_data import load_data
from datetime import datetime

class BasicTestCase(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_homepage(self):
		data = load_data()
		for item in data:
			item['time'] = datetime.strptime(item['time'], '%Y-%m-%d %H:%M:%S')

		res = proxy(WEBSITE_ADDRESS)
		doc = PyQuery(res)

		article_elems = doc('.article-list-item-main')

		titles = sorted([elem.get('data-article-title') for elem in article_elems])
		
		groundtruth = sorted([item['title'] for item in sorted(data, key=lambda i: i['time'], reverse=True)][: len(titles)])

		self.assertTrue(titles == groundtruth)


if __name__ == '__main__':
	unittest.main()

		

