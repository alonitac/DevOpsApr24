import datetime
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.utils import secure_filename
import os
from utils import detect
from prometheus_client import Counter, Summary, make_wsgi_app, Info

app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = 'static/data'

requests_metric = Counter('requests_total', 'HTTP Requests', ['method', 'endpoint'])

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


# Try by from your browser:  localhost:8080
@app.route("/", methods=['GET'])
def home():
    requests_metric.labels(request.method, request.path).inc()
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    p = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(p)
    detections = detect(p)
    return render_template('result.html', filename=f'data/{filename}', detections=detections)


# Try by:  curl -X POST -F 'file=@<local-path-to-image-file>' localhost:8080/api/upload
@app.route('/api/upload', methods=['POST'])
def api_upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    p = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(p)
    detections = detect(p)
    return jsonify(
        {
            "timestamp": datetime.datetime.now().isoformat(),
            "request": {
                "base_url": request.base_url,
                "accept": request.mimetype,
                "status": 200,
                "client_ip": request.remote_addr
            },
            "allowed_types": ['png', 'jpg', 'jpeg', 'gif'],
            "secure": None,
            "detections": detections
        }
    )


# Try by: curl -X POST -H "Content-Type: application/json" -d '{"name": "linuxize", "email": "linuxize@example.com"}' http://localhost:8080/update-profile
@app.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.json
    print(f'Doing something with the data...\n{data}')
    return 'Profile updated!\n'


@app.route('/status')
def status():
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
