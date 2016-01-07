
def get_argument(request, key, default_value=None):
    if key in request.GET:
        return request.GET[key]
    if key in request.POST:
        return request.POST[key]
    return default_value