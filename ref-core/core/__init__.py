# The api module
import flask as fk
from refdb.common.core import setup_app
from refdb.common.models import SetModel
from refdb.common.models import ReferenceModel

import os
import json
import datetime
import traceback

import requests
from datetime import date, timedelta
from functools import update_wrapper

import time

app = setup_app(__name__)

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and fk.request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = fk.make_response(f(*args, **kwargs))
            if not attach_to_all and fk.request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

CORE_VERSION = '0.1'
CORE_URL = '/ref/v{0}'.format(CORE_VERSION)

def core_response(code, title, content):
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

import endpoints
