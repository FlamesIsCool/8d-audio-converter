from flask import Flask, request, send_file, render_template_string, send_from_directory
from pydub import AudioSegment
import os
import math

app = Flask(__name__)
UPLOAD_FOLDER = "."
SEGMENT_MS = 100  # length of each audio segment for panning


def apply_bass_boost(audio: AudioSegment) -> AudioSegment:
    low = audio.low_pass_filter(150)
    boosted = low + 6
    return audio.overlay(boosted)


def apply_reverb(audio: AudioSegment, amount: float) -> AudioSegment:
    if amount <= 0:
        return audio
    decay = amount / 100.0
    delay = 50  # milliseconds
    out = audio
    for i in range(1, 4):
        out = out.overlay(audio - (i * 6 * (1 - decay)), position=i * delay)
    return out

@app.route("/", methods=["GET", "POST"])
def index():
    download_link = None
    speed = request.form.get("speed", "3")
    intensity = request.form.get("intensity", "75")
    reverb = request.form.get("reverb", "40")
    direction = request.form.get("direction", "clockwise")
    bass_boost = request.form.get("bass_boost") is not None
    if request.method == "POST":
        file = request.files["audio"]
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        audio = AudioSegment.from_file(filepath)

        # optional effects
        if bass_boost:
            audio = apply_bass_boost(audio)
        try:
            reverb_val = float(reverb)
        except ValueError:
            reverb_val = 0.0
        audio = apply_reverb(audio, reverb_val)

        # 8D panning
        audio_8d = AudioSegment.empty()
        try:
            speed_val = float(speed)
            if speed_val <= 0:
                speed_val = 3.0
        except ValueError:
            speed_val = 3.0

        try:
            intensity_val = float(intensity) / 100.0
        except ValueError:
            intensity_val = 0.75

        direction_sign = -1 if direction == "counterclockwise" else 1

        for i in range(0, len(audio), SEGMENT_MS):
            segment = audio[i:i + SEGMENT_MS]
            t = i / 1000.0
            pan = math.sin(2 * math.pi * t / speed_val) * intensity_val * direction_sign
            audio_8d += segment.pan(pan)

        output_path = os.path.join(UPLOAD_FOLDER, f"8d_{filename}")
        audio_8d.export(output_path, format="mp3")
        download_link = f"/download/8d_{filename}"

    with open("index.html") as f:
        html = f.read()
    return render_template_string(
        html,
        download_link=download_link,
        speed=speed,
        intensity=intensity,
        reverb=reverb,
        direction=direction,
        bass_boost=bass_boost,
    )

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
