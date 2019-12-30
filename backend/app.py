from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from persistance.persistor import Persistor
from configuration.configurator import Configurator
from sensors.sensors import Sensors
from sensors.dummy import DummySensor
from schedule.sensor_schedule import SensorScheduler

sensor_libs = True
try:
    from sensors.dht import DHT
    from sensors.sds11 import SDS
    from sensors.mq135 import MQSensor
except ImportError:
    sensor_libs = False

app = Flask(__name__)
cors = CORS(app)
config = Configurator()
persistor = Persistor(config)
if sensor_libs:
    mq = MQSensor(cal_dir=config.fullpath)
    dht = DHT()
    sds = SDS(DEBUG=True)
    try:
        sds.cmd_set_sleep(1)
    except Exception as e:
        pass
    sensors = Sensors(mq, dht, sds)
else:
    dummy = DummySensor(caldir=config.fullpath)
    dummy2 = DummySensor(caldir=config.fullpath, name="dummy2")
    sensors = Sensors(dummy, dummy2)

persistor.read_buffer()

scheduler = SensorScheduler(sensors, persistor)
scheduler.scheduler.start()
scheduler.read_and_reschedule()


@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello World!'


@app.route('/data')
@cross_origin()
def read_saved_data():
    return jsonify(is_error=False, data=persistor.read_buffer())


@app.route("/read", methods=["POST"])
@cross_origin()
def read():
    scheduler.read_and_reschedule()
    return jsonify(is_error=False, data=persistor.read_buffer())


@app.route("/configuration", methods=["GET", "POST"])
@cross_origin()
def configure():
    if request.method == "GET":
        return jsonify(is_error=False, data=persistor.config.read())
    if request.method == "POST":
        newconf = request.json
        persistor.config.update(newconf)
        return "OK", 200


@app.route("/calibration", methods=["GET", "POST"])
@cross_origin()
def calibrate():
    if request.method == "GET":
        return jsonify(is_error=False, data={"calibration": sensors.calibration_history()})
    if request.method == "POST":
        sensors.calibrate()
        return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
