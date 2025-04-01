from abc import ABC, abstractmethod
from typing import Tuple
from .models import VoiceCode, SynthAudioOptions

class TTSServiceBase(ABC):
    """Abstract base class for Text-to-Speech services"""
    
    @abstractmethod
    def get_tts(self, 
                   text: str, 
                   voice_name: VoiceCode = None, 
                   options: SynthAudioOptions = None,
                   lang: str = 'en',
                   is_ssml: bool = False) -> Tuple[bytes, str]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            voice_name: Voice identifier to use
            options: Synthesis options like speed, pitch etc
            lang: Language code (default 'en')
            is_ssml: Whether the text is SSML markup
            
        Returns:
            Tuple containing:
            - bytes: The audio content
            - str: The voice name used
        """
        pass 