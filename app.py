# -*- coding: utf-8 -*-

from flask import Flask, request, send_file, make_response
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {
    'avi',
    'mkv',
    'mp4',
    'mpeg',
    'mpg',
    'mov'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def is_allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_request(request):
    if 'file' not in request.files:
        raise ValueError('File extension not allowed')
    file = request.files['file']
    if file.filename == '':
        raise ValueError('Not selected file')
    if not file or  not is_allowed_file(file.filename):
        raise ValueError('File not allowed')

def save_uploaded_file(request):
    file = request.files['file']
    filename = secure_filename(file.filename)
    destiny_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(destiny_path)
    return destiny_path

def get_video_dimensions(filename):
    dimensions_raw = subprocess.run([
        'ffprobe', 
        '-v', 
        'error', 
        '-show_entries', 
        'stream=width,height', 
        '-of', 
        'default=noprint_wrappers=1:nokey=1', 
        filename
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    dimensions = str(dimensions_raw.stdout) \
        .replace('\'', '') \
        .replace('b', '') \
        .split('\\n')
    return (int(dimensions[0]), int(dimensions[1]))

def conver_to_gif(filename):
    dimensions = get_video_dimensions(filename)
    scale = '200:-1'
    if dimensions[1] > dimensions[0]:
        scale = '-1:200'
    convert_command = f'ffmpeg -hide_banner -nostdin -y -i {filename} -b 1000k -vf "scale={scale}" {filename}.gif'
    os.system(convert_command)
    return f'{filename}.gif'

@app.route('/convert_file', methods=['POST'])
def convert_file():
    try:
        validate_request(request)
        destiny_path = save_uploaded_file(request)
        created_gif = conver_to_gif(destiny_path)
        response = send_file(created_gif)
        os.remove(destiny_path)
        os.remove(created_gif)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200
    except ValueError as error:
        print(error)
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.data = str(error)
        return response, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
