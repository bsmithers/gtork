import os

from flask import Flask, render_template, jsonify, request, session

from gtork.garmin.garmin import Garmin, GarminException
from gtork.garmin.parsers import GarminParseException
from gtork.gtork import Activity, Garmin2Runkeeper
from gtork.runkeeper.runkeeper import Runkeeper, RunkeeperException

app = Flask(__name__)
app.config.from_pyfile('../config.py')


@app.route('/')
def list():
    session.pop('garmin_state', None)
    return render_template("list.html", additional_js=['credentials.js', 'activities.js'])


@app.route('/activities', methods=['GET'])
def activities():
    if app.config['DEV'] and os.path.exists('/tmp/garmin.json'):
        import json
        with open('/tmp/garmin.json') as fh:
            return jsonify(json.load(fh))

    try:
        g = Garmin()
        g.login(request.args.get('user'), request.args.get('pass'))
        session['garmin_state'] = g.get_state()
        return jsonify(g.fetch_activities())
    except GarminException as e:
        return jsonify({'error': str(e)}), 400


@app.route('/upload', methods=['POST'])
def upload():
    try:
        activity_id = request.form['id']
        activity_name = request.form['name']
        activity_desc = request.form['description']
        activity_type = request.form['type']
        activity_start = request.form['local_start_time']
        runkeeper_access_token = request.form['access_token']
    except KeyError as e:
        return jsonify({"error": "activity data not provided"}), 400

    activity = Activity(name=activity_name, description=activity_desc, type=activity_type, local_start_time=activity_start)

    try:
        try:
            g = Garmin()
            g.reload_state(session['garmin_state'])
        except KeyError:
            return jsonify({'error': 'No garmin session was found; maybe you need to enable cookies?'}), 400

        garmin_files = g.download_activity(activity_id, app.config['DATA_DIR'])
        with open(garmin_files['gpx']) as gpx_handle, open(garmin_files['tcx']) as tcx_handle:
            gpx_data = gpx_handle.read()
            tcx_data = tcx_handle.read()
            converter = Garmin2Runkeeper(activity, gpx_data, tcx_data)
            json_data = converter.as_rk_dict()
    except GarminException as e:
        return jsonify({'error': 'Error communicating with garmin. Exception: {}'.format(e)}), 400
    except GarminParseException as e:
        return jsonify({'error': 'Error parsing the garmin data. Exception: {}'.format(e)}), 400

    try:
        rk = Runkeeper(runkeeper_access_token)
        rk.upload_activity(json_data)
    except RunkeeperException as e:
        return jsonify({'error': 'Error uploading activity to Runkeeper. Exception: {}'.format(e)}), 400

    return jsonify({'success' : True}), 200

@app.route('/auth', methods=['GET'])
def auth():
    code = request.args.get('code')

    if not code:
        return render_template('auth.html', additional_js=['credentials.js', 'auth.js'])

    # We got a code back from Runkeeper. Complete the authorisation

    client_id = app.config["RUNKEEPER_CLIENT_ID"]
    client_secret = app.config["RUNKEEPER_CLIENT_SECRET"]

    access_token = Runkeeper.complete_authorisation(code, request.base_url, client_id, client_secret)
    r = Runkeeper(access_token)
    real_name = r.get_name()

    return render_template('auth_complete.html', access_token=access_token, real_name=real_name, additional_js=['credentials.js'])


if __name__ == '__main__':
    app.run(debug=True)