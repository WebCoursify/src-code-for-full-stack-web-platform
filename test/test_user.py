from test_model import ModelBaseTestCase
from config import DEFAULT_USER_NAME, WEBSITE_ADDRESS
import requests
from util import random_string
import unittest

class UserBaseTestCase(ModelBaseTestCase):
	pass

class UserTestCase(UserBaseTestCase):

	def register(self, email, username, password):
		return requests.post(WEBSITE_ADDRESS + '/api/register', data={'email': email, 'username': username, 'password': password})

	def test_registration(self):
		print "It should remind me of existed user"
		response = self.register(DEFAULT_USER_NAME + '@gmail.com', DEFAULT_USER_NAME, DEFAULT_USER_NAME)
		self.assertTrue('error' in response.json())

		print "It should successfully register a user"
		username = random_string()
		response = self.register(username + '@gmail.com', username, username)
		self.assertTrue(response.json().get('success', False))

		self.login(email=username + '@gmail.com', password=username)


if __name__ == '__main__':
	unittest.main()