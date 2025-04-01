from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, Response
from openai import OpenAI

from .models import TTSDto, SynthAudioOptions, AudioSpeed
from .speech import get_tts_model

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(prefix='/api/tts-library', tags=['tts-library'])


@router.post('/tts')
async def get_tts(data: TTSDto) -> dict:
    """ Return bytes of audio for the given text"""
    options = SynthAudioOptions(speed=data.speed or AudioSpeed.Regular) 

    tts_model = get_tts_model(text=data.text, voice=data.voice, options=options, provider='google')
    
    if data.speedRate:
        speedRate = 1 + data.speedRate/100
        options.speed_rate = speedRate

    audio_bytes, meta = tts_model.get_tts(text=data.text, voice_name=data.voice, options=options)
    
    print('audio_bytes', 'meta', meta)

    # if data.ssml:
    #     response = tts_model.get_tts(data.ssml, voice=data.voice, is_ssml=True, options=options)
    # else:
    #     response = tts_model.get_tts(data.text, voice=data.voice, options=options)

    if data.generateTranscription:
        print('transcription not implemented')
        transcription = ""
        # try:
        #     file = ('audio.mp3', response[0], "audio/mpeg")

        #     transcription = client.audio.transcriptions.create(
        #         model="whisper-1", 
        #         file=file, 
        #         response_format='verbose_json', 
        #         timestamp_granularities=['word']
        #     )
            
        #     transcription = json.dumps(transcription.model_dump())
        #     print("transcription", transcription)
        # except Exception as e:
        #     print("Some error transcribing", e)
        #     transcription = ""
    else:
        transcription = ""

    return Response(content=audio_bytes, media_type="audio/mpeg", headers={"transcription": transcription})

    