from flask import Flask, request, send_file, render_template_string, send_from_directory
from pydub import AudioSegment
import os
import math

app = Flask(__name__)
UPLOAD_FOLDER = "."
SEGMENT_MS = 100  # length of each audio segment for panning

@app.route("/", methods=["GET", "POST"])
def index():
    download_link = None
    speed = request.form.get("speed", "5")
    if request.method == "POST":
        file = request.files["audio"]
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        audio = AudioSegment.from_file(filepath)
        audio_8d = AudioSegment.empty()
        try:
            speed_val = float(speed)
            if speed_val <= 0:
                speed_val = 5.0
        except ValueError:
            speed_val = 5.0

        for i in range(0, len(audio), SEGMENT_MS):
            segment = audio[i:i+SEGMENT_MS]
            t = i / 1000.0  # time in seconds
            pan = math.sin(2 * math.pi * t / speed_val)
            audio_8d += segment.pan(pan)

        output_path = os.path.join(UPLOAD_FOLDER, f"8d_{filename}")
        audio_8d.export(output_path, format="mp3")
        download_link = f"/download/8d_{filename}"

    with open("index.html") as f:
        html = f.read()
    return render_template_string(html, download_link=download_link, speed=speed)

@app.route("/download/<filename>")
def download(filename):
    return send_file(filename, as_attachment=True)

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

if __name__ == "__main__":
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True)
