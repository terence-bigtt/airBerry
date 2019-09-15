from flask import Flask, jsonify, request
from persistance.persistor import Persistor
from configuration.configurator import Configurator
from sensors.sensors import Sensors
from sensors.dht import DHT
from sensors.sds11 import SDS
from sensors.mq135 import MQSensor
from schedule.sensor_schedule import SensorScheduler

app = Flask(__name__)

config = Configurator()
persistor = Persistor(config)
mq = MQSensor()
dht = DHT()
sds = SDS()
try:
    sds.cmd_set_sleep(1)
except Exception as e:
    pass

sensors = Sensors(mq, dht, sds)

persistor.read_buffer()

scheduler = SensorScheduler(sensors, persistor)
scheduler.scheduler.start()
scheduler.read_and_reschedule()



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/data')
def read_saved_data():
    return jsonify(is_error=False, data=persistor.read_buffer())


@app.route("/configuration", methods=["GET", "POST"])
def configure():
    if request.method == "GET":
        return jsonify(is_error=False, data=persistor.config.read())
    if request.method == "POST":
        newconf = request.json
        persistor.config.update(newconf)
        return 200


@app.route("/calibration", methods=["GET", "POST"])
def calibrate():
    if request.method == "GET":
        return jsonify(is_error=False, data={"calibrated": sensors.calibrated})
    if request.method == "POST":
        sensors.calibrate()
        return 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
