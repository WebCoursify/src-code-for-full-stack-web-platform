import json, urllib, urllib2

def proxy(url, method="get", query={}, post_as_string=False):
    method = method.lower()
    
    if method == "post":
        if post_as_string:
            data = json.dumps(query)
        else:
            data = urllib.urlencode(query)
            req = urllib2.urlopen(url=url, data=data)
    elif method == "get":
        para = urllib.urlencode(query)
        req = urllib.urlopen(url + "?" + para)
    res = req.read()
    res_code = str(req.getcode())
    if res_code[0] != '2':
        raise Exception(res)
        
    return res