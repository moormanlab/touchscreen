from flask import Flask, render_template, flash, request, redirect, url_for, send_file, send_from_directory
import os
#from flask_uploads import UploadSet, configure_uploads

#app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#protocols = UploadSet(name='protocols', extensions=['py'], default_dest='static/protocols')
#app.config["SECRET_KEY"] = os.urandom(24)
#configure_uploads(app, protocols)
from flask_uploads import UploadSet, configure_uploads

app = Flask(__name__)
protocols = UploadSet('protocols', extensions=('py'))
app.config['UPLOADED_PROTOCOLS_DEST'] = 'protocols'
app.config['SECRET_KEY'] = os.urandom(24)

import flaskcode

app.config.from_object(flaskcode.default_config)
app.config['FLASKCODE_RESOURCE_BASEPATH'] = 'protocols'
app.register_blueprint(flaskcode.blueprint, url_prefix='/editor')

configure_uploads(app, protocols)

def make_tree(path):
    tree = dict(name=path, children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        lst.sort()
        for fname in lst:
            fn = os.path.join(path, fname)
            if os.path.isfile(fn) and os.path.splitext(fn)[1]=='.py':
                tree['children'].append(fname)
    return tree


def size_to_str(value):
    if value < 1024:
        return '{:>3d}  B'.format(int(value))
    elif value/1024 < 1024:
        return '{:>3d} kB'.format(int(value/(1024**1)))
    elif value/(1024**2) < 1024:
        return '{:>3d} MB'.format(int(value/(1024**2)))
    elif value/(1024**3) < 1024:
        return '{:>3d} GB'.format(int(value/(1024**3)))
    else: 
        return '{:>3d} TB'.format(int(value/(1024**4)))

LOGPATH = 'logs'
def make_tree_log(path):
    path = LOGPATH
    protocols = dict(name='protocollogs', children=[])
    system = dict(name='systemlogs', children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        lst.sort()
        for fname in lst:
            fn = os.path.join(path, fname)
            if os.path.isfile(fn) and os.path.splitext(fn)[1]=='.log':
                size = os.path.getsize(os.path.abspath(fn))
                sizestr = size_to_str(size)
                if fname.split(sep='-')[-1] == 'system.log':
                    system['children'].append(dict(name=fname,size=sizestr))
                else:
                    protocols['children'].append(dict(name=fname,size=sizestr))
    return protocols, system


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    path = os.path.expanduser('protocols')
    if request.method == 'POST':
        if 'actionFile' in request.form:
            if not ('file' in request.form):
                flash ("Protocol not selected")
            elif request.form['actionFile'] == 'remove':
                filename = request.form['file']
                assert os.path.isfile(os.path.join(path,filename))
                #### TODO generate a way to double confirm the removing
                os.remove(os.path.join(path,filename))
                flash ('Protocol {} removed succesfully'.format(filename))
            elif request.form['actionFile'] == 'edit':
                filename = request.form['file']
                assert os.path.isfile(os.path.join(path,filename))
                #### TODO open editor with filename
            elif request.form['actionFile'] == 'download':
                filename = request.form['file']
                fullpath = os.path.join(os.path.abspath(path),filename)
                assert os.path.isfile(fullpath)
                #### TODO refresh page
                return send_file(fullpath, as_attachment=True, download_name = filename)
            else:
                app.logger('file {} action {}'.format(request.form['file'],request.form['actionFile'])) 
        elif 'newFile' in request.form and 'protocol' in request.files:
            filen = request.files['protocol']
            if filen.filename == '':
                flash('No protocol selected for uploading')
            else:
                newfn=protocols.save(filen)
                if not (newfn == filen.filename):
                    flash('Warning: File already exists, saving with new name: {}'.format(newfn))
                app.logger.info('Protocol uploaded {}'.format(newfn))
    return render_template('manager.html', tree=make_tree(path))



@app.route('/logmanager', methods=['GET', 'POST'])
def logmanager():
    path = os.path.expanduser(LOGPATH)
    if request.method == 'POST':
        if 'actionFile' in request.form:
            app.logger.info(request.form)
            if not ('file' in request.form):
                flash ("log file not selected")
            elif request.form['actionFile'] == 'remove':
                filename = request.form['file']
                assert os.path.isfile(os.path.join(path,filename))
                #### TODO generate a way to double confirm the removing
                os.remove(os.path.join(path,filename))
                flash ('Logfile {} removed succesfully'.format(filename))
            elif request.form['actionFile'] == 'view':
                filename = request.form['file']
                assert os.path.isfile(os.path.join(path,filename))
                #### TODO design log viewer
            elif request.form['actionFile'] == 'download':
                filename = request.form['file']
                fullpath = os.path.join(os.path.abspath(path),filename)
                assert os.path.isfile(fullpath)
                #### TODO refresh page
                return send_file(fullpath, as_attachment=True, download_name = filename)
            else:
                app.logger.info('file {} action {}'.format(request.form['file'],request.form['actionFile'])) 
    ptree,stree = make_tree_log(LOGPATH)
    return render_template('logmanager.html', ptree=ptree,stree=stree)



@app.route('/editor/<filename>')
def editor(filename):
    return 'Editing file'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                          'mouse.xpm',mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
