from flask import Flask, request, send_file, render_template_string
from pydub import AudioSegment
import os

app = Flask(__name__)
UPLOAD_FOLDER = "."

@app.route("/", methods=["GET", "POST"])
def index():
    download_link = None
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

        output_path = os.path.join(UPLOAD_FOLDER, f"8d_{filename}")
        audio_8d.export(output_path, format="mp3")
        download_link = f"/download/8d_{filename}"

    with open("index.html") as f:
        html = f.read()
    return render_template_string(html, download_link=download_link)

@app.route("/download/<filename>")
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
