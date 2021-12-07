import os
from werkzeug.utils import secure_filename
import time
import configparser

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(files):
    if 'file' not in files:
        return {'message': 'No file part'}
    basedir = os.path.abspath(os.path.dirname(__file__))
    files = files.getlist('file')
    filenames = ""
    for file in files:
        if file.filename == '':
            return {'message': 'No image selected for uploading'}
        if file and allowed_file(file.filename):
            filename = secure_filename(time.strftime('%y%m%d%H%M%S') + '_' + file.filename)
            file.save(os.path.join(basedir, config['FILE']['UPLOAD_FOLDER'], filename))
        else:
            return {'message': 'Allowed image types are png, jpg, jpeg and gif'}
        filenames = filenames + '"' + filename + '",'

    return {'message': 'Success', 'filename': filenames}