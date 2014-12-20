from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME, MYSQL_DB_NAME, WEBSITE_ADDRESS, DEFAULT_USER_NAME
import unittest
from util import proxy, md5
from pyquery import PyQuery
from load_data import load_data
from datetime import datetime
import requests, json


def 