from django.http import HttpResponse
from django.test import RequestFactory

from config.middleware import ContentSecurityPolicyMiddleware


def _make_csp_middleware():
    return ContentSecurityPolicyMiddleware(lambda request: HttpResponse())


def test_csp_middleware_adds_header_in_production(settings):
    settings.DEBUG = False
    response = _make_csp_middleware()(RequestFactory().get("/"))
    assert "Content-Security-Policy" in response


def test_csp_middleware_skips_in_debug(settings):
    settings.DEBUG = True
    response = _make_csp_middleware()(RequestFactory().get("/"))
    assert "Content-Security-Policy" not in response
