import os
from enum import Enum

from .auth import create_jwt_token, verify_jwt_token
from fastapi import Request
from jinja2 import pass_context
from sqladmin import Admin as SQLAdmin
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

HOST = os.environ.get('HOST')

if HOST is None:
    raise Exception('You should set environ variable HOST to use core.admin')


class AdminSettings(str, Enum):
    USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    PASSWORD = os.environ.get('ADMIN_PASSWORD', 'qwerty')

    SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'SECRET_KEY')
    BASE_URL = os.environ.get('ADMIN_BASE_URL', '/admin')
    STATIC_URL = os.environ.get('ADMIN_STATIC_URL', '/admin/statics/')

    def __str__(self) -> str:
        return self.value


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username != AdminSettings.USERNAME or password != AdminSettings.PASSWORD:
            return False

        token = create_jwt_token({
            'key': AdminSettings.SECRET_KEY
        })
        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        data = verify_jwt_token(token)
        if not data:
            return False

        if data.get('key') != AdminSettings.SECRET_KEY:
            return False
        return True


@pass_context
def my_url_for(context: dict, name: str, /, **path_params) -> str:
    request: Request = context.get("request")
    url = str(request.url_for(name, **path_params))

    if '/admin/statics/' in url:
        return HOST + AdminSettings.STATIC_URL + path_params['path']

    return url


class Admin:
    def __init__(self, title="Admin", logo_url=None, favicon_url=None, middlewares=None, debug=False, templates_dir="templates"):
        self.authentication_backend = AdminAuth(
            secret_key=AdminSettings.SECRET_KEY)
        self.title = title
        self.logo_url = logo_url
        self.favicon_url = favicon_url
        self.middlewares = middlewares
        self.debug = debug
        self.templates_dir = templates_dir

    def init(self, app, engine):
        admin = SQLAdmin(app, engine, base_url=AdminSettings.BASE_URL, title=self.title, logo_url=self.logo_url, favicon_url=self.favicon_url,
                         middlewares=self.middlewares, debug=self.debug, templates_dir=self.templates_dir, authentication_backend=self.authentication_backend)
        admin.templates.env.globals['url_for'] = my_url_for

        for view in ModelView.__subclasses__():
            admin.add_view(view)
