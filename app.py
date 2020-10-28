# -*- coding: utf-8 -*-

from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {
    'avi',
    'mkv',
    'mp4',
    'mpeg',
    'mpg'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def is_allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/convert_file', methods=['POST'])
def convert_file():
    try:
        if 'file' not in request.files:
            raise ValueError('File extension not allowed')
        file = request.files['file']
        if file.filename == '':
            raise ValueError('Not selected file')
        if not file or  not is_allowed_file(file.filename):
            raise ValueError('File not allowed')

        filename = secure_filename(file.filename)
        destiny_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(destiny_path)
        convert_command = f'ffmpeg -hide_banner -nostdin -y -i {destiny_path} {destiny_path}.gif'
        os.system(convert_command)
        created_gif = f'{destiny_path}.gif'
        response = send_file(created_gif)
        os.remove(destiny_path)
        os.remove(created_gif)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200
    except ValueError as error:
        print(error)
        return str(error), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
