import os

from flask import Flask, render_template, jsonify

from gtork import config
from gtork.garmin.garmin import Garmin

app = Flask(__name__)

app.config.from_pyfile('../config.py')

@app.route('/')
def list():
    return render_template("list.html")


@app.route('/activities', methods=['GET'])
def activities():
    if config.DEV and os.path.exists('/tmp/garmin.json'):
        import json
        with open('/tmp/garmin.json') as fh:
            return jsonify(json.load(fh))

    g = Garmin()
    g.login(app.config["GARMIN_USERNAME"], app.config["GARMIN_PASSWORD"])
    return jsonify(g.fetch_activities())

@app.route('/upload', methods=['POST'])
def upload():
    return ''


if __name__ == '__main__':
    app.run(debug=True)