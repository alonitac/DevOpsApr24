import random
from flask import Flask, Response
from prometheus_client import Counter, Gauge, start_http_server, generate_latest

temperature = 25
humidity = 50


def get_temperature_readings():
    global temperature, humidity
    temperature += random.uniform(-1, 1) * 0.1
    humidity += random.uniform(-1, 1) * 0.1

    temperature = max(10, min(35, temperature))
    humidity = max(40, min(60, humidity))

    response = {"temperature": temperature, "humidity": humidity}
    return response


app = Flask(__name__)

current_humidity = Gauge(
        'current_humidity',
        'the current humidity percentage, this is a gauge as the value can increase or decrease',
        ['field']
)

current_temperature = Gauge(
        'current_temperature',
        'the current temperature in celsius, this is a gauge as the value can increase or decrease',
        ['field']
)


@app.route('/metrics')
def metrics():
    values = get_temperature_readings()
    possible_fields = ['field-1', 'field-2', 'field-3', 'field-4', 'field-5']
    field = random.choice(possible_fields)
    current_humidity.labels(field).set(values['humidity'])
    current_temperature.labels(field).set(values['temperature'])
    return Response(generate_latest(), mimetype=str('text/plain; version=0.0.4; charset=utf-8'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
