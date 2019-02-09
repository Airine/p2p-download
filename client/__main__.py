import sys
sys.path.append('../')
# sys.path.append('./')
import json
import os
import socket
import urllib.parse
import urllib.error
import urllib.request

from flask import Flask, flash
from flask import request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename

from flask_cors import CORS

from util.torrent import Torrent


app = Flask(__name__)
CORS(app)

IP = socket.gethostbyname(socket.gethostname())
PORT = 5001

app.config['UPLOAD_FOLDER'] = 'p2t'
app.config['UUID'] = IP + ':' + str(PORT)

# replace ip below with the ip of tracker
# app.config['TRACKER'] = 'http://10.20.193.197:5000'
#
app.config['TRACKER'] = 'http://10.21.35.242:5000'


@app.route('/')
def index():
    """
    Home page of client, should have entry of adding file
    :return:
    """
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload():
    """
    API for uploading file
    :return:
    """
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    # saving file to local disk
    filename = secure_filename(file.filename)
    _data = file.read()
    file.stream.seek(0)
    torrent = Torrent.create_torrents(filename, _data, name=filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], torrent.digest))
    torrent_filename = filename.replace('.', '_') + '.p2t'
    torrent.dump(os.path.join(app.config['UPLOAD_FOLDER'], torrent_filename))

    # notify the tracker (report)
    try:
        req = urllib.request.Request(urllib.parse.urljoin(app.config['TRACKER'], '/api/report'))
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        _dict = {
            'uuid': app.config['UUID'],
            'torrent': torrent.digest,
            'torrent_url': urllib.parse.urljoin(request.host_url, url_for('download', filename=torrent_filename)),
            'file_url': urllib.parse.urljoin(request.host_url, url_for('download', filename=torrent.digest))
        }
        json_data = json.dumps(_dict).encode('utf-8')  # needs to be bytes
        req.add_header('Content-Length', len(json_data))
        response = urllib.request.urlopen(req, json_data)
    except urllib.error.HTTPError:
        pass
    return redirect(url_for('index'))


@app.route('/p2t/<path:filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='application/octet-stream',
                               as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=PORT)
