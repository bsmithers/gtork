import os

from flask import Flask, render_template, jsonify, request, session

from gtork import config
from gtork.garmin.garmin import Garmin

app = Flask(__name__)
app.secret_key = config.APP_SECRET


@app.route('/')
def list():
    session.pop('garmin_state', None)
    return render_template("list.html")


@app.route('/activities', methods=['GET'])
def activities():
    if config.DEV and os.path.exists('/tmp/garmin.json'):
        import json
        with open('/tmp/garmin.json') as fh:
            return jsonify(json.load(fh))

    g = Garmin()
    g.login(config.GARMIN_USERNAME, config.GARMIN_PASSWORD)
    session['garmin_state'] = g.get_state()
    print("State is:")
    print(session['garmin_state'])
    return jsonify(g.fetch_activities())


@app.route('/upload', methods=['POST'])
def upload():
    try:
        activity_id = request.form['id']
    except KeyError:
        print('no id')
        return jsonify({'error': 'no activity ID specified'}), 400

    try:
        g = Garmin()
        g.reload_state(session['garmin_state'])
    except KeyError:
        print('no session')
        return jsonify({'error': 'No garmin session was found; maybe you need to enable cookies?'}), 400

    g.download_activity(activity_id, config.DATA_DIR)
    return jsonify({'success' : True}), 200


if __name__ == '__main__':
    app.run(debug=True)