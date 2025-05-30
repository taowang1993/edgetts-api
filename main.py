import asyncio
import edge_tts
from flask import Flask, Response, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import os

OUTPUT_FILE = "/tmp/test.mp3"
app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# Update the voice mapping dictionary
OPENAI_TO_EDGE_VOICE_MAP = {
    "alloy": "en-US-AvaMultilingualNeural",
    "echo": "en-US-AndrewMultilingualNeural",
    "fable": "en-US-EmmaMultilingualNeural",
    "onyx": "en-US-BrianMultilingualNeural",
    "nova": "fr-FR-VivienneMultilingualNeural",
    "shimmer": "de-DE-SeraphinaMultilingualNeural",
}

async def stream_audio(text, voice) -> None:
    communicate = edge_tts.Communicate(text, voice)
    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
            yield chunk["data"]


def audio_generator(text, voice):
    loop = asyncio.new_event_loop()
    coroutine = stream_audio(text, voice)
    while True:
        try:
            chunk = loop.run_until_complete(coroutine.__anext__())
            yield chunk
        except StopAsyncIteration:
            break


def make_response(code, message, data=None):
    response = {
        'code': code,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)


@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data['text']
    # voice not required
    voice = data.get('voice', 'en-US-AvaMultilingualNeural')
    file_name = data.get('file_name', OUTPUT_FILE)

    communicate = edge_tts.Communicate(text, voice)
    communicate.save_sync(file_name)
    return send_file(file_name, mimetype='audio/mpeg')


@app.route('/tts/stream', methods=['POST'])
async def stream_audio_route():
    data = request.get_json()
    text = data['text']
    voice = data.get('voice', 'en-US-AvaMultilingualNeural')

    return Response((audio_generator(text, voice)), content_type='application/octet-stream')


@app.route('/voices', methods=['GET'])
async def voices():
    try:
        voices = await edge_tts.list_voices()
        return make_response(200, 'OK', voices)
    except Exception as e:
        return make_response(500, str(e))


async def is_valid_edge_voice(voice_name):
    voices = await edge_tts.list_voices()
    return any(voice["ShortName"] == voice_name for voice in voices)


@app.route('/v1/audio/speech', methods=['POST'])
async def openai_compatible_tts():
    try:
        data = request.get_json()

        # Validate required fields
        if 'input' not in data:
            return make_response(400, 'Missing required field: input')

        text = data['input']
        openai_voice = data.get('voice', 'alloy')

        # First try to map OpenAI voice name, if not found use the provided name directly
        edge_voice = OPENAI_TO_EDGE_VOICE_MAP.get(openai_voice)
        if not edge_voice:
            # If it's not an OpenAI voice name, use it directly but validate it first
            if await is_valid_edge_voice(openai_voice):
                edge_voice = openai_voice
            else:
                return make_response(400, f'Invalid voice name: {openai_voice}. Use /voices endpoint to get list of valid voices.')

        # Return streaming response
        return Response(
            audio_generator(text, edge_voice),
            content_type='audio/mpeg',
            headers={
                'Content-Disposition': 'attachment; filename="speech.mp3"'
            }
        )
    except Exception as e:
        return make_response(500, str(e))


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
