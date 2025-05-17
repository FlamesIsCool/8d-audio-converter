from flask import Flask, render_template, request, send_from_directory
from pydub import AudioSegment
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audio"]
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        audio = AudioSegment.from_file(filepath)
        audio_8d = AudioSegment.empty()

        for i in range(0, len(audio), 200):
            segment = audio[i:i+200]
            pan = ((i // 200) % 40 - 20) / 20
            audio_8d += segment.pan(pan)

        output_path = os.path.join(CONVERTED_FOLDER, f"8d_{filename}")
        audio_8d.export(output_path, format="mp3")

        return render_template("index.html", download_file=f"8d_{filename}")

    return render_template("index.html", download_file=None)

@app.route("/converted/<filename>")
def download(filename):
    return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
