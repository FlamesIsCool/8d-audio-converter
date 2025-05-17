from flask import Flask, request, render_template, send_file
from pydub import AudioSegment
import numpy as np
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Use local ffmpeg binaries in bin/ folder
AudioSegment.converter = "./bin/ffmpeg"
AudioSegment.ffprobe = "./bin/ffprobe"

def apply_8d_effect(audio_path, output_path):
    audio = AudioSegment.from_file(audio_path)
    if audio.channels == 1:
        audio = audio.set_channels(2)
    sample_rate = audio.frame_rate
    sample_width = audio.sample_width
    total_samples = len(audio.get_array_of_samples()) // 2

    samples = np.array(audio.get_array_of_samples()).reshape((-1, 2)).astype(np.float32)
    max_val = 2 ** (8 * sample_width - 1)
    samples = samples / max_val

    t = np.arange(total_samples) / sample_rate
    lfo_freq = 0.08
    lfo = np.sin(2 * np.pi * lfo_freq * t)

    left_gain = np.cos((lfo + 1) * np.pi / 4)
    right_gain = np.sin((lfo + 1) * np.pi / 4)

    max_delay = 5
    left_delay = max_delay * np.maximum(lfo, 0)
    right_delay = max_delay * np.maximum(-lfo, 0)

    indices = np.arange(total_samples).astype(np.float32)
    left_channel = samples[:, 0]
    right_channel = samples[:, 1]
    left_delayed = np.interp(indices, indices - left_delay, left_channel)
    right_delayed = np.interp(indices, indices - right_delay, right_channel)

    processed_left = left_delayed * left_gain
    processed_right = right_delayed * right_gain
    processed_signal = np.vstack((processed_left, processed_right)).T

    peak = np.max(np.abs(processed_signal))
    if peak > 1.0:
        processed_signal = processed_signal / peak

    processed_signal = (processed_signal * max_val).astype(np.int16)
    processed_data = processed_signal.tobytes()

    processed_audio = AudioSegment(
        data=processed_data,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=2
    )
    processed_audio.export(output_path, format="mp3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audiofile"]
        if not file:
            return "No file uploaded."

        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"{filename}_8D.mp3")
        file.save(input_path)

        apply_8d_effect(input_path, output_path)
        return send_file(output_path, as_attachment=True)

    return render_template("index.html")
