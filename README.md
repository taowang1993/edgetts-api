# EdgeTTS API

## Introduction

EdgeTTS API allows you to convert text into speech using a variety of multilingual voices provided by Microsoft TTS Services. This means you can have text read aloud in different languages and accents, making it versatile for various applications.

## Features

- Multilingual
- Natural-sounding
- Streaming (generate chunk by chunk)
- Non-streaming (generate an entire file)
- Deployable with Docker
- Super Fast
- Compatible with OpenAI API

## How It Works

Simply send a text and choose a voice from the available options, and the API will generate an audio output. The process is seamless and can be used for both streaming and non-streaming audio outputs.

## Voices

[voices.yaml](https://github.com/taowang1993/edgetts-api/blob/main/voices.yaml)

en-US-AvaMultilingualNeural
en-US-AndrewMultilingualNeural
en-US-EmmaMultilingualNeural
en-US-BrianMultilingualNeural
fr-FR-VivienneMultilingualNeural
de-DE-SeraphinaMultilingualNeural

## Deployment

### Option 1: Deploy with Python

1. Clone the repository:
```bash
git clone https://github.com/taowang1993/edgetts-api
cd edgetts-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the service:
```bash
python main.py
```

The service will be available at `http://localhost:5000`

### Option 2: Deploy with Docker

1. Build the image:
```bash
docker build -t edgetts-api .
```

2. Run the container:
```bash
docker run -d -p 5000:5000 edgetts-api
```

## API Documentation

### 1. List Available Voices

Retrieves all supported voice options.

```
GET /voices
```

Response example:
```json
{
    "code": 200,
    "message": "OK",
    "data": [
        {
            "Name": "en-US-GuyNeural",
            "ShortName": "en-US-GuyNeural",
            "Gender": "Male",
            "Locale": "en-US"
        },
        // ... more voices
    ]
}
```

### 2. Text-to-Speech (Download)

Convert text to speech and download the audio file.

```
POST /tts
```

Request body:
```json
{
    "text": "Hello, World!",
    "voice": "en-US-AvaMultilingualNeural"    // Optional, defaults to "en-US-AvaMultilingualNeural"
}
```

Note: The `file_name` parameter is optional and will default to a temporary file if not provided.

Response:
- Content-Type: audio/mpeg
- Returns audio file stream

### 3. Text-to-Speech (Streaming)

Convert text to speech with streaming output.
Choose this endpoint for real-time playback.

```
POST /tts/stream
```

Request body:
```json
{
    "text": "Hello, World!",
    "voice": "en-US-AvaMultilingualNeural"    // Optional, defaults to "en-US-AvaMultilingualNeural"
}
```

Response:
- Content-Type: application/octet-stream
- Returns audio stream

### OpenAI-compatible Streaming

Convert text to speech with streaming output.
This endpoint is compatible with the OpenAI TTS API format.

```
POST /v1/audio/speech
```

Request body:
```json
{
    "model": "tts-1",              // Optional and currently ignored
    "input": "Hello, World!",      // Required: text to convert to speech
    "voice": "alloy"               // Optional, defaults to "alloy"
}
```

Voice Mappings:
| OpenAI Voice | EdgeTTS Voice |
|--------------|----------------|
| alloy | en-US-AvaMultilingualNeural |
| echo | en-US-AndrewMultilingualNeural |
| fable | en-US-EmmaMultilingualNeural |
| onyx | en-US-BrianMultilingualNeural |
| nova | fr-FR-VivienneMultilingualNeural |
| shimmer | de-DE-SeraphinaMultilingualNeural |

Response:
- Content-Type: audio/mpeg
- Returns audio stream

Example usage with OpenAI Python client:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:5000/v1",  // Your edgetts url
    api_key="your_api_key_here"  // Required but not used
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world!"
)

# Save the audio to a file
response.stream_to_file("output.mp3")
```

## Usage Examples

### Python

```python
import requests

# Get available voices
response = requests.get('http://localhost:5000/voices')
voices = response.json()['data']

# Text-to-Speech (Download)
data = {
    "text": "Hello, World!",
    "voice": "en-US-AvaMultilingualNeural",
    "file_name": "output.mp3"
}
response = requests.post('http://localhost:5000/tts', json=data)
with open('output.mp3', 'wb') as f:
    f.write(response.content)

# Text-to-Speech (Streaming)
response = requests.post('http://localhost:5000/tts/stream', json=data, stream=True)
with open('stream_output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

### Curl

```bash
# Get available voices
curl http://localhost:5000/voices

# Text-to-Speech (Download)
curl -X POST http://localhost:5000/tts \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello, World!", "voice":"en-US-AvaMultilingualNeural"}' \
    --output output.mp3

# Text-to-Speech (Streaming)
curl -X POST http://localhost:5000/tts/stream \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello, World!", "voice":"en-US-AvaMultilingualNeural"}' \
    --output stream_output.mp3
```

## License

[MIT License](LICENSE)
