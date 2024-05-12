from django.http import HttpRequest


def refresh_session(request: HttpRequest):
    from importlib import import_module

    from django.conf import settings

    engine = import_module(settings.SESSION_ENGINE)
    SessionStore = engine.SessionStore
    session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
    request.session = SessionStore(session_key)
    return request


def get_session_var(request: HttpRequest, key, default=None):
    request = refresh_session(request)
    if default is not None:
        return request.session.get(key, default)
    else:
        return request.session[key]


def set_session_var(request: HttpRequest, key, value):
    request.session[key] = value
    request.session.save()

    return request
