from enum import Enum
from typing import Optional

from pydantic import BaseModel

class VoiceType(str, Enum):
    RegularMan = 'Regular Man'
    RegularWoman = 'Regular Woman'
    YoungWoman = 'Young Woman'
    YoungMan = 'Young Man'
    TeenagerMan = 'Teenager Man'
    TeenagerWoman = 'Teenager Woman'
    ChildGirl = 'Child Girl'
    ChildBoy = 'Child Boy'
    ManStudio = 'ManStudio'
    Man2Studio = 'Man2Studio'
    WomanStudio = 'WomanStudio'

class VoiceCode(str, Enum):
    ManStudioQ = "en-US-Studio-Q",
    WomanStudioQ = "en-US-Studio-O",
    ManJourneyD = "en-US-Journey-D",
    WomanJourneyF = "en-US-Journey-F",
    ManCasualK = "en-US-Casual-K",
    ManNeural2A = "en-US-Neural2-A", 
    WomanNeural2C = 'en-US-Neural2-C',
    ManNeural2D = 'en-US-Neural2-D',
    WomanNeural2E = 'en-US-Neural2-E',
    WomanNeural2F = 'en-US-Neural2-F',
    WomanNeural2G = 'en-US-Neural2-G',
    WomanNeuralH = 'en-US-Neural2-H',
    ManNeural2I = 'en-US-Neural2-I',
    ManNeural2J = 'en-US-Neural2-J',
    ManNewsN = 'en-US-News-N',
    WomanNewsL = 'en-US-News-L'

class StorageFile(BaseModel):
    # name: str = None i can extract easy from path, not sure if a should keep name 
    bucket: str = None
    path: str = None
    url: str = None


class StorageAudioSynth(StorageFile):
    text: str = None
    speed: str = None
    # voiceType: Optional[str] # voy a reservar voice type para nombres internos, voice code es el de google
    voiceCode : Optional[str] = None


class AudioSpeed(str, Enum):
    VerySlow = "verySlow",
    Slow = "slow",
    Regular = "regular",
    Fast = "fast",
    VeryFast = "veryFast"

    
class SynthAudioOptions(BaseModel):
    speed: AudioSpeed = None
    speed_rate: float = None

