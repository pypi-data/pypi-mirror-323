import os, concurrent.futures, threading, json, queue, time
from typing import List, Dict, Any, Union, ClassVar, BinaryIO, Optional
from . import client as _client, utils, afritextai_types as _types


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
                   configurations: Optional[_types.TranscriptConfig] = None,
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
        if not configurations:
            configurations = self.configurations

        if isinstance(data, str):
            with open(data, "rb") as audio_file:
                data = audio_file
        return self.transcribe_file(
            audio_file=data,
            configurations=configurations,
            pool=True,
        )
            


    def _transcript_from_file(self, data: Union[str, BinaryIO]) -> str:
        """
        Uploads an audio file.

        Args:
            data (Union[str, BinaryIO]): The audio file to upload.
        Returns:
                str: The URL of the uploaded file.
        """
        if isinstance(data, str):
            with open(data, "rb") as audio_file:
                return utils.get_transcript(
                    client=self._client.http_client,
                    audio_file=audio_file,
                )
        else:
            return utils.upload_file(
                client=self._client.http_client,
                audio_file=data,
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
        return self._transcript_from_file(
            data=audio_file,
            configurations=configurations,
            pool=pool,
        )
