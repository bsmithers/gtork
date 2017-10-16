import os

from flask import Flask, render_template, jsonify, request, session

from gtork import config
from gtork.garmin.garmin import Garmin
from gtork.gtork import Activity, Garmin2Runkeeper

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
        activity_name = request.form['name']
        activity_desc = request.form['description']
        activity_type = request.form['type']
        activity_start = request.form['local_start_time']
    except KeyError:
        return jsonify({"error": "activity data not provided"}), 400

    activity = Activity(name=activity_name, description=activity_desc, type=activity_type, local_start_time=activity_start)

    try:
        g = Garmin()
        g.reload_state(session['garmin_state'])
    except KeyError:
        return jsonify({'error': 'No garmin session was found; maybe you need to enable cookies?'}), 400

    garmin_files = g.download_activity(activity_id, config.DATA_DIR)
    with open(garmin_files['gpx']) as gpx_handle, open(garmin_files['tcx']) as tcx_handle:
        gpx_data = gpx_handle.read()
        tcx_data = tcx_handle.read()
        converter = Garmin2Runkeeper(activity, gpx_data, tcx_data)
        json_data = converter.as_json()
        print(json_data)

    return jsonify({'success' : True}), 200


if __name__ == '__main__':
    app.run(debug=True)