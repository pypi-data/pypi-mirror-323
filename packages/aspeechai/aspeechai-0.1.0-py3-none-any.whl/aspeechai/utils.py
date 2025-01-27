from typing import List, Dict, Any, Union, ClassVar, BinaryIO, Optional
from urllib.parse import urlencode

import httpx

ENDPOINT_TRANSCRIPT = "/v1/transcript/"


def get_transcript(
    client: httpx.Client,
    audio_file: BinaryIO = None,
    audio_url: str = None,
    speech_model: str = None,
    language_code: str = None,
) -> Dict[str, Any]:
    """
    Get a transcription from an audio file.

    Args:
        client (httpx.Client): The HTTP client.
        audio_file (BinaryIO): The audio file to transcribe.
        audio_url (str): The URL of the audio file to transcribe.
        speech_model (str): The speech model to use for the transcription.
        language_code (str): The language code of the transcription.
    Returns:
        Dict[str, Any]: The transcription.
    """
    if audio_file:
        files = {'audio_file': audio_file}
    body = {
        "speech_model": speech_model,
        "language_code": language_code,
    }
    response = client.post(
        ENDPOINT_TRANSCRIPT,
        data=body,
        files=files,
    )
    print('Response: ', response)
    # Close the file after request if opened
    if audio_file:
        audio_file.close()
    # if response.status_code != httpx.codes.OK:
    #     response.raise_for_status()

    return response.status_code,  response.json()