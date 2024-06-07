# make a simple flask upload server for testing purposes only

from psutil import disk_usage 
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import logging

from ftplib import FTP
import ftplib
import urllib

from time import time

# import socket
# import shutil

DOWNLOAD_INTERVAL = 0

UPLOAD_FOLDER = Path('./Upload').resolve()
directory = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mp3', 'ogg', 'm4a', 'avi', 'mov', 'zip', 'rar', '7z', 'tar', 'gz', 'iso', 'apk', 'exe', 'msi', 'deb', 'pkg', 'dmg', 'bin', 'bat', 'sh', 'py', 'c', 'cpp',
                         'java', 'js', 'html', 'htm', 'css', 'scss', 'json', 'xml', 'csv', 'xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx', 'pdf', 'csv', 'db', 'dbf', 'log', 'mdb', 'sav', 'sql', 'tar', 'xml', 'apk', 'bat', 'bin', 'com', 'exe', 'jar', 'ai'])
ROOT = Path("./static").resolve()

error = "<html><head><title>{status}</title></head><body><center><h1>{status}</h1></center><hr><center>{server}</center></body></html>"

#app = Flask(__name__)
#app = Flask(__name__, template_folder=f"{path}")
app = Flask(__name__, template_folder=ROOT)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
#=========================================================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#=========================================================

def get_files(path, sort_by='mtime'):
    """
    Returns a list of all files in the specified directory
    and its subdirectories, including their full paths,
    that are not currently being modified.
    """
    files = []
    current_time = time()
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            stat = os.stat(full_path)
            modified_time = stat.st_mtime if sort_by == 'mtime' else stat.st_ctime
            if (current_time - modified_time) > DOWNLOAD_INTERVAL:
                files.append((full_path, modified_time))
    return sorted(files, key=lambda x: x[1], reverse= True)
#=========================================================

def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)} {SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'
#=========================================================

@app.route('/')
def index():
    return (ROOT / 'index.html').resolve().read_bytes() 
#=========================================================

@app.route('/', methods=['POST', 'PUT'])
def upload():
    f = request.files['file']
    if f.filename == '':
        return redirect(url_for('list_files'))
    save_path = UPLOAD_FOLDER / f.filename
    f.save(save_path)
    #return 'File uploaded successfully'
    return redirect(url_for('list_files'))

#=========================================================

@app.route('/', methods=['GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded successfully'
            
#=========================================================

@app.route('/list')
def list_files():
    total, used, free , disk = disk_usage('/')
    files = get_files(UPLOAD_FOLDER, sort_by='mtime')
    file_links = []
    file_names = []
    file_path = []
    file_size = []
    for file in files:
        file_path.append(file[0])
        #encoded_filename = urllib.parse.quote(file[0])
        #file_links.append(url_for('download', filename=encoded_filename))      
        file_links.append(url_for('download', filename=os.path.basename(file[0])))    
        file_names.append(os.path.basename(file[0]))
        size = os.path.getsize(file[0])
        size = get_readable_file_size(size)
        file_size.append(size)
        #print('file_name = ', os.path.basename(file[0]))
        #print('file_links = ', url_for('download', filename=os.path.basename(file[0])))
    Avail_Files = len(file_names)
    Avail_Storage = get_readable_file_size(free)
    data = zip(file_names, file_links, file_path, file_size)    
    return render_template('list.html', data=data, Avail_Files = Avail_Files, Avail_Storage = Avail_Storage)
#=========================================================

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    """Download a file."""
    logging.info('Downloading file= [%s]', filename)
    logging.info(app.root_path)
    full_path = os.path.join(app.root_path, UPLOAD_FOLDER)
    logging.info(full_path)
    #print('full_path = ', full_path)
    #print('filename = ', filename)
    return send_from_directory(full_path, filename, as_attachment=True)
#=========================================================

@app.route('/delete', methods=['POST'])
def delete_files():
    file_names = request.form.getlist('delete_file')
    for file_name in file_names:
        filepath = file_name
        #=== Not work =================================
        # if filepath.lower().startswith(directory.lower()):
        #     if os.path.isdir(filepath):
        #         shutil.rmtree(filepath)
        #     else:
        #         os.remove(filepath)
        #=== Instead that =============================
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)     
        #==============================================         
    return redirect(url_for('list_files'))
#=========================================================

@app.route('/assets/<path:filename>')
def send_assets(filename):
    
    file=ROOT / 'assets' /filename
    if file.exists():
        return file.read_bytes()
    else:
        return error.format(status="404", server=request.url), 404
#=========================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)   
    #app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)    
#=========================================================
