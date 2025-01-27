import httpx, threading, json, os
from typing import List, Dict, Any, Union, ClassVar, Optional
from .__version__ import __version__    


class Client:
    _default: ClassVar[Optional["Client"]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self, 
                    token: Optional[str] = None,
                    email: Optional[str] = None,
                    http_timeout: Optional[int] = 60,
                    base_url: str = "https://api.a-speechai.com",
                    token_required: bool = True,
                    email_required: bool = True,
                    **kwargs: Any) -> None:

                """
                Initializes the client with the necessary parameters.

                Args:
                    token (Optional[str]): The token to use for authentication.
                    http_timeout (Optional[int]): The timeout for the HTTP requests.
                    base_url (str): The base URL for the API.
                    token_required (bool): Whether a token is required for authentication.
                """
                if token_required and not token:
                    raise ValueError("Please provide a token for authentication.")
                if email_required and not email:
                    raise ValueError("Please provide an email for authentication.")

                user_agent = f"{httpx._client.USER_AGENT} A-SpeechAI/1.0 (sdk=Ptyhon/{__version__})"
                headers = {
                    "User-Agent": user_agent,
                }
                if token:
                    headers["X-API-Key"] = token
                if email:
                    headers["X-User-Email"] = email

                self._http_client = httpx.Client(
                    base_url=base_url,
                    headers=headers,
                    timeout=http_timeout,
                )
    @property
    def http_client(self) -> httpx.Client:
        """
        Returns the HTTP client.
        """
        return self._http_client


