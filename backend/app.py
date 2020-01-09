import logging

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from configuration.configurator import Configurator
from persistance.diskwriter import DiskWriterMessages
from schedule.sensor_schedule import SensorScheduler
from sensors.sensors import SensorsMessages

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

cors = CORS(app)
config = Configurator(app.logger)
scheduler = SensorScheduler(config, app.logger)

scheduler.start()

@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello World!'


@app.route('/data')
@cross_origin()
def read_saved_data():
    return jsonify(is_error=False, data=scheduler.diskpersistor.ask(DiskWriterMessages.READ, block=True))


@app.route("/read", methods=["POST"])
@cross_origin()
def read():
    scheduler.read_and_reschedule()
    return jsonify(is_error=False)


@app.route("/configuration", methods=["GET", "POST"])
@cross_origin()
def configure():
    if request.method == "GET":
        return jsonify(is_error=False, data=config.read())
    if request.method == "POST":
        newconf = request.json
        scheduler.update(newconf)
        return "OK", 200


@app.route("/calibration", methods=["GET", "POST"])
@cross_origin()
def calibrate():
    if request.method == "GET":
        return jsonify(is_error=False, data={"calibration": scheduler.sensors.calibration_history()})
    if request.method == "POST":
        scheduler.sensors.ask(SensorsMessages.CALIBRATE).calibrate()
        return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
