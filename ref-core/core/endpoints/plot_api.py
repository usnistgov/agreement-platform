import json

from flask.ext.api import status
import flask as fk

from core import app, CORE_URL, crossdomain, core_response
from refdb.common.models import SetModel
from refdb.common.models import ReferenceModel

import mimetypes
import json
import traceback
import datetime
import random
import string
import os
import thread
from StringIO import StringIO
from utils import Build, SetPlot

@app.route(CORE_URL + '/plot/set/<set_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def plot_set(set_id):
    if fk.request.method == 'GET':
        _set = SetModel.objects(id=set_id).first()
        if _set:
            if _set.status == 'empty':
                 return core_response(204, 'Nothing done', 'No data in this set.')
            else:
                file_buffer = None
                try:
                    set_plot = SetPlot(set_id)
                    set_plot.plot()
                    filename = 'set-{0}.png'.format(set_id)
                    with open('plots/{0}'.format(filename), 'r') as _file:
                        file_buffer = StringIO(_file.read())
                    file_buffer.seek(0)
                except:
                    print traceback.print_exc()
                if file_buffer != None:
                    os.remove('plots/{0}'.format(filename))
                    return fk.send_file(file_buffer, attachment_filename=filename, mimetype='image/png')
                else:
                    return core_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            return core_response(204, 'Nothing done', 'Could not find this set.')
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/plot/raw/<ref_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def plot_raw(ref_id):
    if fk.request.method == 'GET':
        _ref = ReferenceModel.objects(id=ref_id).first()
        if _ref:
            if _ref.status != 'done':
                 return core_response(204, 'Nothing done', 'No graph generated yet. This reference is not finished yet.')
            else:
                file_buffer = None
                try:
                    filename = 'ref-{0}.png'.format(ref_id)
                    with open('plots/{0}'.format(filename), 'r') as _file:
                        file_buffer = StringIO(_file.read())
                    file_buffer.seek(0)
                except:
                    print traceback.print_exc()
                if file_buffer != None:
                    return fk.send_file(file_buffer, attachment_filename=filename, mimetype='image/png')
                else:
                    return core_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            return core_response(204, 'Nothing done', 'Could not find this reference.')
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/plot/stats/<ref_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def plot_stats(ref_id):
    if fk.request.method == 'GET':
        _ref = ReferenceModel.objects(id=ref_id).first()
        if _ref:
            if _ref.status != 'done':
                 return core_response(204, 'Nothing done', 'No graph generated yet. This reference is not finished yet.')
            else:
                file_buffer = None
                try:
                    filename = 'stats-ref-{0}.png'.format(ref_id)
                    with open('plots/{0}'.format(filename), 'r') as _file:
                        file_buffer = StringIO(_file.read())
                    file_buffer.seek(0)
                except:
                    print traceback.print_exc()
                if file_buffer != None:
                    return fk.send_file(file_buffer, attachment_filename=filename, mimetype='image/png')
                else:
                    return core_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            return core_response(204, 'Nothing done', 'Could not find this reference.')
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
