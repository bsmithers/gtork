from flask import Flask, render_template, jsonify

from gtork.garmin.garmin import Garmin

app = Flask(__name__)

app.config.from_pyfile('../config.py')

@app.route('/')
def upload():
    return render_template("list.html")


@app.route('/activities', methods=['GET'])
def activities():
    g = Garmin()
    g.login(app.config["GARMIN_USERNAME"], app.config["GARMIN_PASSWORD"])
    return jsonify(g.fetch_activities())


if __name__ == '__main__':
    app.run(debug=True)