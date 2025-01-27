import os, concurrent.futures, threading, json, queue, time, logging
from typing import List, Dict, Any, Union, ClassVar, BinaryIO, Optional
from . import client as _client, utils, aspeechai_types as _types

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Transcriber:
    """
    A class for transcribing audio files.
    """

    def __init__(self,
                client: Optional[_client.Client] = None,
                configurations: Optional[_types.TranscriptConfig] = None,
                max_workers: Optional[int] = None,
    ) -> None:
        """
        Initializes the transcriber with the necessary parameters.

        Args:
            client (Optional[_client.Client]): The HTTP client.
            configurations (Optional[_types.TranscriptConfig]): The configurations for the transcription.
            max_workers (Optional[int]): The maximum number of workers to use for transcription.


        Example:
        
        """
        self.client = client or _client.Client()
        self.configurations = configurations
        
        if not max_workers:
            self.max_workers = max(1, os.cpu_count() - 1)

        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
        )


    def transcribe(self,
                   data: Union[BinaryIO, str],
                   speech_model: Optional[str] = None,
                   language_code: Optional[str] = None,
                   audio_file: Optional[str] = None,
                   audio_url: Optional[str] = None,
                #    configurations: Optional[_types.TranscriptConfig] = None,
                   ) -> Dict[str, Any]:
        """
        Transcribes an audio file which can be a file or a URL.

        Args:
            audio_file (BinaryIO): The audio file to transcribe.
            configurations (Optional[_types.TranscriptConfig]): The configurations for the transcription.
            pool (bool): Whether to use a thread pool for transcription.

        Returns: 
            Dict[str, Any]: The transcription.
        """
        configurations = _types.TranscriptConfig(
            speech_model=speech_model,
            language_code=language_code,
            audio_file=audio_file,
            audio_url=audio_url,
        )

        if isinstance(data, str):
            with open(data, "rb") as audio_file:
                data = audio_file
                return self.transcribe_file(
                    audio_file=data,
                    configurations=configurations,
                    pool=True,
                )
            


    def _transcript(self,
                    data: Union[str, BinaryIO],
                    configurations: Optional[_types.TranscriptConfig] = None,
                    ) -> str:
        """
        Uploads an audio file.

        Args:
            data (Union[str, BinaryIO]): The audio file to upload.
        Returns:
                str: The URL of the uploaded file.
        """
        logger.info("Transcribing audio file: %s", data)
        if isinstance(data, str):
            with open(data, "rb") as audio_file:
                return utils.get_transcript(
                    client=self.client.http_client,
                    audio_file=audio_file,
                    speech_model=configurations.speech_model,
                    language_code=configurations.language_code
                )
        else:
            return utils.get_transcript(
                client=self.client.http_client,
                audio_file=data,
                speech_model=configurations.speech_model,
                language_code=configurations.language_code
            )


    def transcribe_file(self,
                        audio_file: BinaryIO,
                        configurations: Optional[_types.TranscriptConfig] = None,
                        pool: bool = True
                        ) -> Dict[str, Any]:
        """
        Transcribes an audio file.

        Args:
            audio_file (BinaryIO): The audio file to transcribe.
            configurations (Optional[_types.TranscriptConfig]): The configurations for the transcription.
            pool (bool): Whether to use a thread pool for transcription.

        Returns:
            Dict[str, Any]: The transcription.
        """
        return self._transcript(
            data=audio_file,
            configurations=configurations,
            # pool=pool,
        )
