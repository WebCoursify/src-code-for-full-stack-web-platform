from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS, DEFAULT_USER_NAME
import unittest
from util import proxy, md5
from pyquery import PyQuery
from load_data import load_data
from datetime import datetime
import requests, json
import uuid



class HeartBeatTestCase(unittest.TestCase):

	def test_heart_beat(self):
		HEART_BEAT_URL = WEBSITE_ADDRESS + '/practise/heartbeat'

		for i in range(100):
			random_str = str(uuid.uuid1())
			response = requests.get(HEART_BEAT_URL, params={'username': random_str})
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.text, '<b>%s</b>' % (random_str), "response unmatched: %s" %(random_str))

		response = requests.get(HEART_BEAT_URL)
		self.assertEqual(response.status_code, 400, "Doesn't return 400")

		response = requests.post(HEART_BEAT_URL)
		self.assertEqual(response.status_code, 405, "Doesn't return 405")


class FilesTestCase(unittest.TestCase):

	def test_files(self):
		def get_file_url(file_id):
			return '%s/practise/file/%s/get' % (WEBSITE_ADDRESS, file_id)

		CREATE_FILE_URL = WEBSITE_ADDRESS + '/practise/file/create'
		testfile_path = 'resources/test3.jpg'

		file_ids = []
		for i in range(10):
			res = requests.post(CREATE_FILE_URL, files={'file': open(testfile_path, 'rb')})

			self.assertEqual(res.status_code, 200)
			data = res.json()
			self.assertTrue('id' in data)
			file_ids.append(data['id'])

		md5_val = md5(open(testfile_path, 'rb').read())

		for id in file_ids:
			res = requests.get(get_file_url(id))

			returned_md5 = md5(res.content)

			self.assertEqual(md5_val, returned_md5, 'md5 unmatched')

		response = requests.post(get_file_url(1))
		self.assertEqual(response.status_code, 405, 'Should return 405')

		response = requests.get(get_file_url(1))
		self.assertEqual(response.status_code, 404, 'Should return 404')

