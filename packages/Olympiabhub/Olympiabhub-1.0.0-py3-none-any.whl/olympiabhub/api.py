import os
import requests
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class OlympiaAPI:
    """
    A class for interacting with the Olympia API, providing access to LLM and embedding models.

    This class handles both direct API calls and requests through a Nubonyxia proxy, offering
    methods for text generation and embedding creation.

    Args:
        model (str): The model identifier to use for generating responses or embeddings.
        token (str, optional): The API authentication token. If not provided, will attempt to read
            from OLYMPIA_API_KEY or OLYMPIA_API_TOKEN environment variables.
        proxy (str, optional): The proxy URL to use for Nubonyxia requests. If not provided,
            will attempt to read from PROXY environment variable.
        base_url (str, optional): The base URL for the Olympia API.
        user_agent (str, optional): The user agent string used for Nubonyxia requests.

    Raises:
        ValueError: If no token is provided and none can be found in environment variables.

    Attributes:
        token (str): The API authentication token.
        model (str): The selected model identifier.
        base_url (str): The base URL for the Olympia API.
        nubonyxia_proxy (str): The configured proxy URL for Nubonyxia requests.
        nubonyxia_user_agent (str): The user agent string used for Nubonyxia requests.

    Example:
        >>> api = OlympiaAPI(model="gpt-3.5", token="your-api-token")
        >>> response = api.Chat("Hello, how are you?")
        >>> embeddings = api.create_embedding(["Text to embed"])
    """

    def __init__(
        self, 
        model: str, 
        token: str = None, 
        proxy: str = None,
        base_url: str = "https://api.olympia.bhub.cloud",
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
    ):
        self.token = (
            token or os.getenv("OLYMPIA_API_KEY") or os.getenv("OLYMPIA_API_TOKEN")
        )
        if not self.token:
            raise ValueError(
                "Token is required. Set OLYMPIA_API_KEY/OLYMPIA_API_TOKEN or pass as parameter."
            )

        self.model = model
        self.base_url = base_url
        self.nubonyxia_proxy = proxy or os.getenv("PROXY")
        self.nubonyxia_user_agent = user_agent

    def _get_headers(self) -> Dict[str, str]:
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self, method: str, endpoint: str, data: Dict = None, use_proxy: bool = False
    ) -> Any:
        url = f"{self.base_url}/{endpoint}"
        session = requests.Session() if use_proxy else requests

        if use_proxy and self.nubonyxia_proxy:
            session.get_adapter("https://").proxy_manager_for(
                f"http://{self.nubonyxia_proxy}"
            ).proxy_headers["User-Agent"] = self.nubonyxia_user_agent
            session.proxies.update(
                {"http": self.nubonyxia_proxy, "https": self.nubonyxia_proxy}
            )

        try:
            response = session.request(
                method=method, url=url, headers=self._get_headers(), json=data
            )
            
            # Tentative de récupération du message d'erreur JSON
            try:
                response_json = response.json()
            except:
                response_json = None

            if not response.ok:
                error_message = "Unknown error"
                if response_json and "error" in response_json:
                    if isinstance(response_json["error"], dict):
                        error_message = response_json["error"].get("message", "Unknown error")
                    else:
                        error_message = str(response_json["error"])
                elif response_json and "message" in response_json:
                    error_message = response_json["message"]
                
                logger.error(f"API error: {error_message} (Status code: {response.status_code})")
                raise ValueError(f"API error: {error_message} (Status code: {response.status_code})")

            return response_json if response_json else response.json()

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(f"Failed to connect to {url}: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            raise TimeoutError(f"Request to {url} timed out: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise RuntimeError(f"Request to {url} failed: {e}")
        except ValueError as e:
            # Réémission des erreurs ValueError (qui incluent nos erreurs API personnalisées)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError(f"Unexpected error occurred: {e}")


    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 1,
        n: int = 1,
        stream: bool = False,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> Dict[str, Any]:
        """OpenAI-style chat completion endpoint."""
        data = {
            "messages": messages,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        return self._make_request(
            method="POST",
            endpoint="v1/chat/completions",
            data=data,
            use_proxy=False,
        )

    def chat_completion_nubonyxia(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 1,
        n: int = 1,
        stream: bool = False,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> Dict[str, Any]:
        """OpenAI-style chat completion endpoint using Nubonyxia proxy."""
        data = {
            "messages": messages,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        return self._make_request(
            method="POST",
            endpoint="v1/chat/completions",
            data=data,
            use_proxy=True,
        )

    def completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 1,
        n: int = 1,
        stream: bool = False,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> Dict[str, Any]:
        """OpenAI-style completion endpoint."""
        data = {
            "prompt": prompt,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        return self._make_request(
            method="POST",
            endpoint="v1/completions",
            data=data,
            use_proxy=False,
        )

    def completion_nubonyxia(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        top_p: float = 1,
        n: int = 1,
        stream: bool = False,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
    ) -> Dict[str, Any]:
        """OpenAI-style completion endpoint using Nubonyxia proxy."""
        data = {
            "prompt": prompt,
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "n": n,
            "stream": stream,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        return self._make_request(
            method="POST",
            endpoint="v1/completions",
            data=data,
            use_proxy=True,
        )

    def embedding(self, texts: List[str]) -> Dict[str, Any]:
        """OpenAI-style embedding endpoint."""
        if not texts or not all(isinstance(text, str) for text in texts):
            raise ValueError("Texts must be a non-empty list of strings")
        return self._make_request(
            method="POST",
            endpoint="v1/embeddings",
            data={"model": self.model, "input": texts},
            use_proxy=False,
        )

    def embedding_nubonyxia(self, texts: List[str]) -> Dict[str, Any]:
        """OpenAI-style embedding endpoint using Nubonyxia proxy."""
        if not texts or not all(isinstance(text, str) for text in texts):
            raise ValueError("Texts must be a non-empty list of strings")
        return self._make_request(
            method="POST",
            endpoint="v1/embeddings",
            data={"model": self.model, "input": texts},
            use_proxy=True,
        )

    def get_llm_models(self) -> List[str]:
        """Get available LLM models."""
        return self._make_request(
            method="GET", 
            endpoint="modeles",
            use_proxy=False
        )["modèles"]

    def get_llm_models_nubonyxia(self) -> List[str]:
        """Get available LLM models using Nubonyxia proxy."""
        return self._make_request(
            method="GET", 
            endpoint="modeles",
            use_proxy=True
        )["modèles"]

    def get_embedding_models(self) -> List[str]:
        """Get available embedding models."""
        return self._make_request(
            method="GET", 
            endpoint="embeddings",
            use_proxy=False
        )["modèles"]

    def get_embedding_models_nubonyxia(self) -> List[str]:
        """Get available embedding models using Nubonyxia proxy."""
        return self._make_request(
            method="GET", 
            endpoint="embeddings",
            use_proxy=True
        )["modèles"]
