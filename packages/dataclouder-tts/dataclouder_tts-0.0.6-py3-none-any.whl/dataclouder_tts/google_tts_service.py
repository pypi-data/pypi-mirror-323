import random
from google.cloud import texttospeech
from typing_extensions import TypedDict

from .models import AudioSpeed, GoogleVoiceOptions, VoiceCode, SynthAudioOptions, VoiceOption, VoiceSettings
from .tts_service_base import TTSServiceBase

class GoogleTTSService(TTSServiceBase):
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    def get_voice_options(self, voice_name: VoiceCode = None, lang='en') -> VoiceOption:
        if voice_name is None:
            print('Voice name is None')
            # Is not id, means the best quality voice, try to use always an id
            voice_options = [voice for voice in GoogleVoiceHQOptions if lang in voice['lang']]
            voice_data = random.choice(voice_options)
            voice_name = voice_data['id']
            language_code = voice_data['lang']
        else:
            voice = [item for item in GoogleVoiceOptions if item['id'] == voice_name]
            if len(voice) <= 1:
                return voice[0]
            
        default_voice_id = 'en-US-Journey-F'
        print('Voice not found giving default voice', default_voice_id)
        voice_options = [voice for voice in GoogleVoiceOptions if default_voice_id == voice['id']]
        return voice_options[0]

    def get_tts(self, text: str, voice_name: VoiceCode = None, options: SynthAudioOptions = None, 
                  lang='en', is_ssml=False) -> tuple[bytes, VoiceOption]:
        
        print('Voice name:', voice_name, 'Options:', options, 'Lang:', lang, 'is_ssml:', is_ssml)

        voice_options = self.get_voice_options(voice_name, lang)
            
        speaking_rate = 1
        
        # TODO: pending check speed rate
        # if options and 'Journey' not in voice_name:
        #     if options.speed_rate and options.speed_rate > 0:
        #         speaking_rate = options.speed_rate
        #     else:
        #         speaking_rate = self.get_speed_rate(options.speed)

        if is_ssml:
            synthesis_input = texttospeech.SynthesisInput(ssml=text)
        else:
            synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_options['lang'], 
            name=voice_options['id']
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16, 
            speaking_rate=speaking_rate
        )

        response = self.client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )
        
        return response.audio_content, voice_options

    @staticmethod
    def get_speed_rate(speed: AudioSpeed) -> float:
        speaking_rate = 1
        if speed == AudioSpeed.VeryFast:
            speaking_rate = 1.50
        if speed == AudioSpeed.Fast:
            speaking_rate = 1.25
        elif speed == AudioSpeed.Regular:
            speaking_rate = 1.0
        elif speed == AudioSpeed.Slow:
            speaking_rate = 0.75
        elif speed == AudioSpeed.VerySlow:
            speaking_rate = 0.50
        return speaking_rate

    def list_voices(self, language_code='en-US'):
        response = self.client.list_voices(language_code=language_code)
        voices = sorted(response.voices, key=lambda voice: voice.name)

        print(f" Voices: {len(voices)} ".center(60, "-"))
        for voice in voices:
            languages = ", ".join(voice.language_codes)
            name = voice.name
            gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
            rate = voice.natural_sample_rate_hertz
            print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

    def text_to_wav(self, voice_name: str, text: str):
        language_code = "-".join(voice_name.split("-")[:2])
        text_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code, 
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=-1.0,
            speaking_rate=0.90
        )

        response = self.client.synthesize_speech(
            input=text_input, 
            voice=voice_params, 
            audio_config=audio_config
        )

        filename = f"{language_code}.wav"

        with open(filename, "wb") as out:
            out.write(response.audio_content)
            print(f'Generated speech saved to "{filename}"')
        
        
