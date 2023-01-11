import cv2
import pyzbar.pyzbar
from flask import Flask, render_template, jsonify
from flask_basicauth import BasicAuth
from flask import Response


app = Flask(__name__)

# Initialize the video capturer, the list of scanned QR code data, and BasicAuth
capturer = cv2.VideoCapture(0)
scanned_data = []
app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = 'ps'
basic_auth = BasicAuth(app)

@app.route('/')
def index():
    # Render the template
    return render_template('index.html')

@app.route('/data')
def data():
    # Find QR codes in the latest frame
    _, frame = capturer.read()
    qr_codes = pyzbar.pyzbar.decode(frame)
    for qr_code in qr_codes:
        # Convert the QR code data to a Unicode string
        data = qr_code.data
        unicode_data = data.decode('utf-8')

        # Add the QR code data to the list of scanned QR code data
        # if it hasn't been added before
        if unicode_data not in scanned_data:
            scanned_data.append(unicode_data)

    # Return the scanned QR code data as JSON
    return jsonify(scanned_data)

@app.route('/video_feed')
@basic_auth.required
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    def generate():
        """Video streaming generator function."""
        while True:
            # Capture frame-by-frame
            ret, frame = capturer.read()
            if ret:
                # encode as jpeg
                ret, jpeg = cv2.imencode('.jpg', frame)
                if ret:
                    # return current frame
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
                else:
                    print('Failed to encode frame as jpeg')
                    break
            else:
                print('Failed to capture frame')
                break
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video')
@basic_auth.required
def video():
    """Render the video feed template"""
    return render_template('video.html')

@app.route('/code_status')
def code_status():
    return render_template('code_status.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
