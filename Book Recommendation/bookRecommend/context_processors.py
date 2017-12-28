from django.conf import settings


def baseurl(request):
    """
    Return a BASE_URL template context for the current request.
    """
    if request.is_secure():
        scheme = 'https://'
    else:
        scheme = 'http://'

    return {'BASE_URL': scheme + request.get_host() + '/'}


def s3url(request):
    return {'S3_URL': settings.S3_URL}