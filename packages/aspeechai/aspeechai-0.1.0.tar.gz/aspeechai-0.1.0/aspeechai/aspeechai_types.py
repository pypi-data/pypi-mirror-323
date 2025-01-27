
from typing import Optional

class TranscriptConfig:
    """
    Configuration for the transcript API
    """
    def __init__(self,
                 speech_model: Optional[str] = None,
                language_code: Optional[str] = None,
                audio_file: Optional[str] = None,
                audio_url: Optional[str] = None,
    ):
        """
        Initializes the transcriber with the necessary parameters.

        Args:
            speech_model (Optional[str]): The speech model to use for the transcription.
            language_code (Optional[str]): The language code of the transcription.
            audio_file (Optional[str]): The audio file to transcribe.
            audio_url (Optional[str]): The audio URL to transcribe.
        """
        self.speech_model = speech_model
        self.language_code = language_code
        self.audio_file = audio_file
        self.audio_url = audio_url