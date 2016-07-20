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
from utils import Build, Evaluation
from openpyxl import load_workbook

@app.route(CORE_URL + '/home', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home():
    if fk.request.method == 'GET':
        _refs = [r for r in ReferenceModel.objects()]
        _ref = _refs[-1]
        print str(_ref.id)
        if _ref:
            if _ref.status != 'done':
                 return core_response(204, 'Nothing done', 'No graph generated yet. This reference is not finished yet.')
            else:
                file_buffer = None
                try:
                    filename = 'error-{0}.png'.format(str(_ref.id))
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


@app.route(CORE_URL + '/home/sets', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_sets():
    if fk.request.method == 'GET':
        sets = [_set.summary() for _set in SetModel.objects()]
        return core_response(200, 'All sets.', sets)
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/home/reference/sets', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_reference_sets():
    if fk.request.method == 'GET':
        refs = [r for r in ReferenceModel.objects()]
        _ref = refs[-1]
        if _ref is None:
            return core_response(404, 'Request suggested an empty response', 'Unable to find the newest reference.')
        else:
            sets = []
            for _set_id in _ref.sets['sets']:
                _set = SetModel.objects.with_id(_set_id['id'])
                if _set:
                    sets.append(_set.summary())
            return core_response(200, 'Reference [{0}] sets.'.format(str(_ref.id)), sets)
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/home/reference/next', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_reference_next():
    if fk.request.method == 'GET':
        new_ref = ReferenceModel.objects(status='new').first()
        if new_ref:
            sets = []
            for _set_id in new_ref.sets['sets']:
                _set = SetModel.objects.with_id(_set_id['id'])
                if _set:
                    sets.append(_set)
            try:
                # build
                # maybe run a daemon
                build = Build(new_ref)
                build.compute()
                build.plot_all()
                build.plot_stat()
                build.plot_bars()
                for _set in sets:
                    _set.status = 'used'
                    _set.save()
                new_ref.status = 'done'
                new_ref.save()
                return fk.redirect('http://0.0.0.0:4000/')
                # return core_response(200, 'Build done.', 'Reference [{0}] was successfully built.'.format(str(new_ref.id)))
            except:
                print traceback.print_exc()
                print "reference build failed."
                return core_response(500, 'Error occured', 'Failed to build this reference.')
            # return core_response(200, 'Existing new reference found','The reference [{0}] was already created and not used.'.format(str(new_ref.id)))
        else:
            _ref, created = ReferenceModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()))
            if created:
                sets = []
                for _set in SetModel.objects():
                    if _set.status != 'excluded':
                        if str(_set.id) not in sets:
                            if _set.updated_from:
                                sets.remove(_set.updated_from)
                                sets.append(str(_set.id))
                            else:
                                sets.append(str(_set.id))
                if len(sets) > 0:
                    _sets = []
                    for _set in sets:
                        set_ = SetModel.objects.with_id(_set)
                        set_.status = "locked"
                        set_.save()
                        if set_:
                            _sets.append({'id':str(set_.id), 'filename':set_.filename})
                    _ref.sets = {'size':len(_sets), 'sets':_sets}
                    _ref.save()
                    sets = []
                    for _set_id in _ref.sets['sets']:
                        _set = SetModel.objects.with_id(_set_id['id'])
                        if _set:
                            sets.append(_set)
                    try:
                        # build
                        # maybe run a daemon
                        build = Build(_ref)
                        build.compute()
                        build.plot_all()
                        build.plot_stat()
                        build.plot_bars()
                        for _set in sets:
                            _set.status = 'used'
                            _set.save()
                        _ref.status = 'done'
                        _ref.save()
                        return fk.redirect('http://0.0.0.0:4000/?reload=true')
                    except:
                        print traceback.print_exc()
                        print "reference build failed."
                        return core_response(500, 'Error occured', 'Failed to build this reference.')
                else:
                    return core_response(204, 'Creation failed','No data sets provided.')
            else:
                return core_response(204, 'Creation failed','Could not create a new reference.')
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/home/reference/evaluate', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_reference_evaluate_data():
    if fk.request.method == 'POST':
        refs = [r for r in ReferenceModel.objects()]
        _ref = refs[-1]
        if _ref is None:
            return core_response(404, 'Request suggested an empty response', 'Unable to find the newest reference.')
        else:
            if fk.request.files:
                file_obj = fk.request.files['file']
                file_name = file_obj.filename
                _set, created = SetModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()))
                if created:
                    _set.filename = '{0}-{1}'.format(str(_set.id), file_name)
                    file_path = '/tmp/{0}'.format(_set.filename)
                    try:
                        with open(file_path, 'wb') as set_file:
                            set_file.write(file_obj.read())
                        wb = load_workbook(file_path, read_only=True)
                        ws = wb.active
                        pressure = {'aliq1':{'run1':[], 'run2':[]}, 'aliq2':{'run1':[], 'run2':[]}}
                        uptake = {'aliq1':{'run1':[], 'run2':[]}, 'aliq2':{'run1':[], 'run2':[]}}
                        for odx, row in enumerate(ws.rows):
                            if odx >= 2:
                                # print "--- row ---"
                                if row[0].value is not None:
                                    pressure['aliq1']['run1'].append(row[0].value)
                                if row[1].value is not None:
                                    uptake['aliq1']['run1'].append(row[1].value)
                                
                                if row[3].value is not None:
                                    pressure['aliq1']['run2'].append(row[3].value)
                                if row[4].value is not None:
                                    uptake['aliq1']['run2'].append(row[4].value)
                                

                                if row[7].value is not None:
                                    pressure['aliq2']['run1'].append(row[7].value)
                                if row[8].value is not None:
                                    uptake['aliq2']['run1'].append(row[8].value)
                                
                                if row[10].value is not None:
                                    pressure['aliq2']['run2'].append(row[10].value)
                                if row[11].value is not None:
                                    uptake['aliq2']['run2'].append(row[11].value)

                        evaluation = Evaluation(eval_id=_set.filename, reference=_ref, pressure=pressure, uptake=uptake)
                        evaluation.run()
                        # print str(evals)
                        os.remove(file_path)
                        _set.delete()
                        reslt_path = evaluation.error()
                        file_buffer = None
                        try:
                            with open(reslt_path, 'r') as _file:
                                file_buffer = StringIO(_file.read())
                            file_buffer.seek(0)
                        except:
                            print traceback.print_exc()
                        if file_buffer != None:
                            # os.remove(reslt_path)
                            return fk.send_file(file_buffer, as_attachment=True, attachment_filename=reslt_path.split('/')[1], mimetype='image/png')
                        else:
                            return core_response(404, 'Request suggested an empty response', 'Unable to return plot image.')
                    except:
                        print traceback.print_exc()
                        _set.delete()
                        print "An error occured!!"
                        return core_response(204, 'Nothing created', 'An error occured.')
                else:
                    return core_response(204, 'Already exists', 'This should normaly never happened.')
            else:
                return core_response(204, 'Nothing created', 'You must a set file.')

    return """
    <!doctype html>
    <html>
        <head>
          <!-- css  -->
          <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
          <link href="http://0.0.0.0:4000/css/materialize.min.css" type="text/css" rel="stylesheet" media="screen,projection"/>
          <link href="http://0.0.0.0:4000/css/style.css" type="text/css" rel="stylesheet" media="screen,projection"/>

          <!--Let browser know website is optimized for mobile-->
          <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no"/>
          <title>Reference Platform</title>
        </head>
        <body>
            <nav class="white" role="navigation">
                <div class="nav-wrapper container">
                  <a id="logo-container" href="http://0.0.0.0:4000" class="teal-text text-lighten-2">Reference</a>
                </div>
            </nav>
            <div class="valign center-align">
                <h1>Upload dataset</h1>
                <form action="" method=post enctype=multipart/form-data>
                    <input type=file name=file>
                    <input type=submit value=Upload>
                </form>
            </div>
            <!--Import jQuery before materialize.js-->
            <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.1.min.js"></script>
            <script type="text/javascript" src="http://0.0.0.0:4000/js/materialize.min.js"></script>
        </body>
    </html>
    
    """

@app.route(CORE_URL + '/home/set/exclude/<set_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_set_exclude(set_id):
    if fk.request.method == 'GET':
        _set = SetModel.objects.with_id(set_id)
        if _set is None:
            return core_response(404, 'Request suggested an empty response', 'Unable to find this set.')
        else:
            if _set.status != 'excluded':
                _set.status = 'excluded'
                _set.save()
                return fk.redirect('http://0.0.0.0:4000/sets')
            else:
                return core_response(204, 'Exclusion failed', 'Set [{0}] is already excluded'.format(_set.filename))
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CORE_URL + '/home/set/include/<set_id>', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_set_include(set_id):
    if fk.request.method == 'GET':
        _set = SetModel.objects.with_id(set_id)
        if _set is None:
            return core_response(404, 'Request suggested an empty response', 'Unable to find this set.')
        else:
            if _set.status == 'excluded':
                _set.status = 'included'
                _set.save()
                return fk.redirect('http://0.0.0.0:4000/sets')
            else:
                return core_response(204, 'Inclusion failed', 'Set [{0}] is not excluded'.format(_set.filename))
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')