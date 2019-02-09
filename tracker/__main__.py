import sys
sys.path.append('../')
# sys.path.append('./')
import json
import random
from collections import defaultdict

from flask import Flask
from flask import request, render_template
from werkzeug import exceptions as flask_exceptions

from util import crossdomain

seeders = defaultdict(dict)

app = Flask(__name__)


@app.route('/api/report', methods=['POST'])
@crossdomain(origin='*')
def report():
    """
    api report route
    adding status of torrent seeding into seeders
    :return: a JSON string with success field
    """
    _data = request.json
    try:
        seeders[_data['torrent']][_data['uuid']] = _data
        return json.dumps({'success': True})
    except flask_exceptions.BadRequestKeyError:
        return json.dumps({'success': False, 'msg': 'Invalid request'})


@app.route('/api/query')
@crossdomain(origin='*')
def query():
    """
    api query route
    query for a torrent status
    example:
     - /api/query?torrent=cf457c98-b37b-4758-b63a-a21ee6aac63f
     - /api/query?torrent=bf65dc58-0c5d-4403-9da1-2056c1231b4d&limit=5
    :return: a JSON array of seeding clients
    """
    _data = request.args
    try:
        limit = len(seeders[_data['torrent']])
        try:
            if _data['limit'] and _data['limit'] < limit:
                limit = _data['limit']
        except flask_exceptions.BadRequestKeyError:
            pass
        _seeders = list(seeders[_data['torrent']].values())
        random.shuffle(_seeders)
        return json.dumps(random.sample(_seeders, limit))
    except flask_exceptions.BadRequestKeyError:
        return json.dumps({'success': False, 'msg': 'Invalid request'})
    except KeyError:
        return json.dumps([])


@app.route('/')
def index():
    # TODO: Complete statics view
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
