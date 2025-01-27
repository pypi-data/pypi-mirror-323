from typing import List, Dict, Any, Union, ClassVar, BinaryIO, Optional
from urllib.parse import urlencode

import httpx

ENDPOINT_TRANSCRIPT = "/v1/transcript"


def get_transcript(
    client: httpx.Client,
    audio_file: BinaryIO,
) -> Dict[str, Any]:
    """
    Get a transcription from an audio file.

    Args:
        client (httpx.Client): The HTTP client.
        audio_file (BinaryIO): The audio file to transcribe.

    Returns:
        Dict[str, Any]: The transcription.
    """
    response = client.post(
        ENDPOINT_TRANSCRIPT,
        content=audio_file,
    )
    if response.status_code != httpx.codes.OK:
        response.raise_for_status()

    return response.json()