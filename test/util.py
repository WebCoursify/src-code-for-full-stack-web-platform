import json, urllib, urllib2
import hashlib
import unittest
import requests
from config import WEBSITE_ADDRESS, DEFAULT_USER_NAME

def md5(stream):
    m = hashlib.md5()
    m.update(stream)
    return m.hexdigest()

def proxy(url, method="get", query={}, post_as_string=False):
    method = method.lower()
    valid_query = {}
    for key, val in query.items():
        if val is not None:
            valid_query[key] = val
            
    if method == "post":
        if post_as_string:
            data = json.dumps(valid_query)
        else:
            data = urllib.urlencode(valid_query)
            req = urllib2.urlopen(url=url, data=data)
    elif method == "get":
        para = urllib.urlencode(valid_query)
        req = urllib.urlopen(url + "?" + para)
    res = req.read()
    res_code = str(req.getcode())
    if res_code[0] != '2':
        raise Exception(res)

    return res

class BaseTestCase(unittest.TestCase):
    def login(self, email=None, password=None):
        if email is None or password is None:
            email = DEFAULT_USER_NAME + '@gmail.com'
            password = md5(DEFAULT_USER_NAME)

        session = requests.Session()

        res = session.get('%s/api/login?email=%s&password=%s' %(WEBSITE_ADDRESS, email, password))
        result = res.json()

        self.assertEqual(result.get('success', None), True)
        return session