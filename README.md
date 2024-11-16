# Edge-TTS API

This project converts Edge-TTS into an API that includes an OpenAI-compatible endpoint.

## Features

- Multilingual Voices from Microsoft TTS Services
- Both Streaming and Non-streaming Audio Output
- Docker Deployment Support
- Low Latency
- OpenAI TTS API Compatibility

## Quick Start

### Option 1: Run Directly

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
    "voice": "en-US-GuyNeural",    // Optional, defaults to "zh-CN-YunxiNeural"
    "file_name": "hello.mp3"       // Optional, defaults to "test.mp3"
}
```

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
    "voice": "en-US-GuyNeural"    // Optional, defaults to "zh-CN-YunxiNeural"
}
```

Response:
- Content-Type: application/octet-stream
- Returns audio stream

### OpenAI-compatible Streaming Endpoint

Convert text to speech with streaming output.
This endpoint is compatible with the OpenAI TTS API format.
It works similar to the /tts/stream endpoint.

```
POST /v1/audio/speech
```

Request body:
```json
{
    "model": "tts-1",              // Optional, currently ignored
    "input": "Hello, World!",      // Required: text to convert to speech
    "voice": "alloy"               // Optional, defaults to "alloy"
}
```

Supported voices and their mappings:
- alloy → en-US-AvaMultilingualNeural
- echo → en-US-AndrewMultilingualNeural
- fable → en-US-EmmaMultilingualNeural
- onyx → en-US-BrianMultilingualNeural
- nova → fr-FR-VivienneMultilingualNeural
- shimmer → de-DE-SeraphinaMultilingualNeural

You can send the default OpenAI voice names with the OpenAI client.
edgetts-api will map the OpenAI voice names to the Edge-TTS voices.

Response:
- Content-Type: audio/mpeg
- Returns audio stream

Example usage with OpenAI Python client:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:5000/v1",  # Your edge-tts url
    api_key="your_api_key_here"  # Required but not used
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

### Python Example

```python
import requests

# Get available voices
response = requests.get('http://localhost:5000/voices')
voices = response.json()['data']

# Text-to-Speech (Download)
data = {
    "text": "Hello, World!",
    "voice": "en-US-GuyNeural",
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

### Curl Example

```bash
# Get available voices
curl http://localhost:5000/voices

# Text-to-Speech (Download)
curl -X POST http://localhost:5000/tts \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello, World!", "voice":"en-US-GuyNeural"}' \
    --output output.mp3

# Text-to-Speech (Streaming)
curl -X POST http://localhost:5000/tts/stream \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello, World!", "voice":"en-US-GuyNeural"}' \
    --output stream_output.mp3
```

## FAQ

1. **Q: How do I choose the right voice?**  
   A: Use the `/voices` endpoint to get a list of all available voices. Choose based on the Locale and Gender attributes.

2. **Q: What languages are supported?**  
   A: Multiple languages including English, Chinese, Japanese, and more. Check the `/voices` endpoint for a complete list.

3. **Q: What is the audio file format?**  
   A: The service generates MP3 audio files.

## Notes

- Docker deployment is recommended for production environments
- The service has a text length limit; consider splitting long texts
- The default port is 5000, configurable through environment variables

## License

[MIT License](LICENSE)
