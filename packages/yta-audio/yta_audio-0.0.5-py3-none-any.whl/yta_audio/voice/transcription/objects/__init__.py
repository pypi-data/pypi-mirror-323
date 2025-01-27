from dataclasses import dataclass
from typing import Union


@dataclass
class AudioTranscriptionWordTimestamp:
    """
    Class that holds the start and the end moment
    of a word said in a timestamped audio
    transcription.
    """

    start: any
    # TODO: Please set the 'start' timestamp type
    """
    The moment in which the word starts being said.
    """
    end: any
    # TODO: Please set the 'start' timestamp type
    """
    The moment in which the word ends being said.
    """

    def __init__(self, start: any, end: any):
        # TODO: Please set the 'start' and 'end' timestamp type
        self.start = start
        self.end = end

@dataclass
class AudioTranscriptionWord:
    """
    Class that holds an audio transcription word
    and also its timestamp, that could be None if
    it is a non-timestamped audio transcription.
    """

    word: str
    """
    The word itself as a string.
    """
    timestamp: Union[AudioTranscriptionWordTimestamp, None]
    """
    The time moment in which the 'word' is said.
    """

    def __init__(self, word: str, timestamp: Union[AudioTranscriptionWordTimestamp, None] = None):
        self.word = word
        self.timestamp = timestamp

@dataclass
class AudioTranscription:
    """
    Class that holds information about an audio
    transcription, including words.
    """

    words: list[AudioTranscriptionWord]
    """
    The list of words.
    """

    @property
    def transcription(self):
        """
        Get the audio transcription as a single string
        which is all the words concatenated.
        """
        return ' '.join([
            word.word
            for word in self.words
        ])

