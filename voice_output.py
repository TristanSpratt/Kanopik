from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import os
from dotenv import load_dotenv

load_dotenv()
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Voice specs:
voice_id = "JBFqnCBsd6RMkjVDRZzb"
model_id="eleven_flash_v2" 

def speak_text(text):
    audio_stream = elevenlabs.text_to_speech.stream(
        text=text,
        voice_id=voice_id,
        model_id=model_id
    )
    stream(audio_stream)