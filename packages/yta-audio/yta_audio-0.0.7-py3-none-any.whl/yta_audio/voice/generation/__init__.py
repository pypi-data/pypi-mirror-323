from yta_general_utils.programming.parameter_validator import PythonValidator
from yta_general_utils.temp import create_temp_filename
from yta_audio.voice.generation.coqui import narrate as narrate_coqui
from yta_audio.voice.generation.google import narrate as narrate_google
from yta_audio.voice.generation.microsoft import narrate as narrate_microsoft
from yta_audio.voice.generation.open_voice import narrate as narrate_open_voice
from yta_audio.voice.generation.tetyys import narrate_tetyys
from yta_audio.voice.generation.tiktok import narrate_tiktok
from yta_audio.voice.generation.tortoise import narrate as narrate_tortoise
from yta_audio.voice.generation.ttsmp3 import narrate_tts3
from abc import ABC, abstractmethod
from typing import Union


class VoiceNarrator(ABC):
    """
    Class to simplify and encapsulate the voice
    narration functionality.
    """

    @abstractmethod
    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        """
        Create a voice narration of the given 'text' and
        stores it locally in the 'output_filename'
        provided (or in a temporary file if not provided).
        """
        pass

class CoquiVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_coqui(text, output_filename)
    
class GoogleVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'language' and 'tld' as parameters
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_google(text, output_filename)
    
class MicrosoftVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'language' and 'tld' as parameters
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_microsoft(text, output_filename)
    
class OpenVoiceVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'speed' as parameter
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_open_voice(text, output_filename)
    
class TetyysVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'speed' as parameter
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_tetyys(text, output_filename)
    
class TiktokVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'speed' as parameter
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_tiktok(text, output_filename)
    
class TortoiseVoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'speed' as parameter
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_tortoise(text, output_filename)
    
class Ttsmp3VoiceNarrator(VoiceNarrator):

    @staticmethod
    def narrate(
        text: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Include 'speed' as parameter
        if not PythonValidator.is_string(text):
            raise Exception('No valid "text" parameter provided.')
        
        if output_filename is None:
            output_filename = create_temp_filename('coqui_narration.mp3')
        
        return narrate_tts3(text, output_filename)