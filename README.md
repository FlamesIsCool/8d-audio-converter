# 8D Audio Converter

This simple Flask web app converts uploaded audio files into an 8D version using [pydub](https://github.com/jiaaro/pydub). The pan effect now uses a smooth sine wave so the audio moves naturally between ears. The web UI also shows a loading bar while processing and lets you choose how fast the audio rotates.

## Requirements

- Python 3.7+
- `ffmpeg` installed on your system (required by pydub)

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Running

Start the server with Python:

```bash
python app.py
```

By default the server listens on `0.0.0.0:5000`. You can customize the host or port using environment variables:

```bash
HOST=0.0.0.0 PORT=8080 python app.py
```

Open the URL in a browser, upload an MP3 or WAV file, set a transition speed if desired, and download the generated 8D audio.
