from abc import ABC, abstractmethod


class AudioTranscriptor(ABC):
    """
    Abstract class to be inherited by audio
    transcriptors that do not include timestamps.
    """

    @abstractmethod
    @staticmethod
    def transcribe(
        audio: any,
        initial_prompt: str
    ):
        """
        Transcribe the provided 'audio' with the help of
        the 'initial_prompt' if provided and get the
        transcripted text.
        """
        pass

class TimestampedAudioTranscriptor(ABC):
    """
    Abstract class to be inherited by audio
    transciptors that include timestamps.
    """

    @abstractmethod
    @staticmethod
    def transcribe(
        audio: any,
        initial_prompt: str
    ):
        """
        Transcribe the provided 'audio' with the help of
        the 'initial_prompt' if provided and get the
        transcripted text with the time moments in which
        each word is detected.
        """
        pass

# TODO: Create the Whisper classes here by
# using the single methods in 'whisper' module