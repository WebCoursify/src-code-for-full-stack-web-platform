
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import redirect


def heart_beat(request):
    """
    Heart beat request:
    :param request contains a parameter named "username"
    :return a http response with html text <b>{username}</b>
    Only allow http get method. If the request is made with some other method, return HttpResponseNotAllowed(405)
    When the request doesn't contain the appropriate parameter, return HttpResponseBadRequest(400)
    """
    # TODO: Implement me
    return None


def create_file(request):
    """
    :param request: contains a file stream named "file"
    :return: a json string looks like {"id": the unique id created for this file}
    You may implement this anyway you want, just remember you'll need to implement another controller,
    which takes the id as parameter, and return the file content. We think one way to implement this is:
    1. Create an unique id in place
    2. Save the file in the local file system, with a path that can be retrieved by the unique id
    3. Return the unique id(which should contains only alphanumeric characters)
    """
    # TODO: Implement me
    return None


def get_file(request, file_id):
    """
    :param request: the request object
    :param file_id: the unique id for the file
    :return: the http response contains the file content.
    Only support GET method.
    When the file cannot be found (i.e. the id is invalid), return HttpResponseNotFound

    There are two possible ways to implement this, according to our knowledge
    1.  Directly read the file stream from where it's saved, and attached the binary file stream to the HttpResponse.
        To do this you might need to set the header appropriately
    2.  Save the file to a place which can be directly served by the Django server.
        Take a look at the MEDIA_ROOT and MEDIA_URL options for Django settings.py. It's something very similar
        to the STATIC_ROOT and STATIC_URL, but for dynamic contents.
        A file saved in the media directory can be directly accessed given the relative url, so you can use
        "redirect"
    """
    # TODO: Implement me
    return None