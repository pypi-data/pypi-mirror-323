from .models import SynthAudioOptions

# from .google_tts_service import get_speech

from .google_tts_service import GoogleTTSService
from .tts_service_base import TTSServiceBase

def get_tts_model(text: str, provider: str = 'google', voice: str = None, is_ssml: bool = False, options: SynthAudioOptions = None) -> TTSServiceBase:
    """
    Get text-to-speech audio bytes
    Returns tuple of (audio_bytes, duration)
    """
    print('get_tts_model', text, voice, options, is_ssml)
    return GoogleTTSService()




# def get_tts(text: str, voice: str = None, provider = "google", options = None, lang = 'en', is_ssml=False) -> tuple[bytes, str]:
#     """ usually Use to generate good voices """

#     if provider == "openai":
#         return openai_service.get_speech(text, voice)
#     elif provider == "google":
#         return google_ai_service.get_speech(text, voice, options, lang, is_ssml)
#     elif provider == "elevenlabs":
#         return eleven_labs.get_speech(text, voice)
#     elif provider == "playht":
#         return playht_service.get_speech(text, voice)