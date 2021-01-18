from getpass import getpass
from typing import Optional

import dotenv
import requests
from requests.exceptions import RequestException

from dolipy.config import DoliConfig


class DolibarrClient:
    """
    Class that communicates with the dolibarr rest API.
    It is designed to just login and retrieve the list of invoices.

    Params:
    ----------------------------------------------------------------
    api_key: str -> API Key for dolibarr rest api [`None`].
    prompt: bool -> Whether or not to prompt the user [`False`].
    cache: bool -> Store the api_key in th configuration file [`False`].
    """
    def __init__(self, api_key: Optional[str] = None, prompt: bool = False, cache: bool = False) -> None:
        self.cnf: DoliConfig = DoliConfig()
        self.prompt: bool = prompt
        self.cache: bool = cache
        self.api_key: str = api_key or self._authenticate()

    @staticmethod
    def _cache_api_key(api_key: str) -> None:
        """
        Saves the api key to the configuration file.

        Params:
        ----------------------------------------------
        api_key: str -> The api key to be stored.
        """
        env_file = dotenv.find_dotenv()
        dotenv.set_key(env_file, "API_KEY", api_key)

    def _authenticate(self) -> str:
        """
        Authenticates self to against dolibarr api.
        If the api_key is passed or cached in the configuration
        it just returns the value. If it is not it will prompt
        the user to pass username and password. In the last case
        if prompt is false it will raise a `ValueError`.
        """
        if api_key := self.cnf.api_key:
            return api_key
        if not self.prompt:
            raise ValueError("Please provide an API Key or set prompt to True")

        resp = self.login()

        api_key = resp['success']['token']

        if self.cache:
            self._cache_api_key(api_key=api_key)

        return resp['success']['token']

    def call(self, method: str = "GET", endpoint: str = '', body: Optional[dict] = None,
             params: Optional[dict] = None) -> dict:
        """
        Generic call method that wraps the `request.request` method.
        It is used by more special methods to communicate with dolibarr rest api.

        Params:
        ------------------------------------------------------------------------
        method: str -> The http method to be used at the call.
        endpoint: str -> The endpoint to be called from the method.
        body: dict -> The body of the call.
        params: dict -> The url params to be included in the call.
        """
        if not body:
            body = {}

        headers = {}
        if not endpoint == 'login':
            headers = {
                'DOLAPIKEY': self.api_key,
                'Accept': 'application/json'
            }

        response = requests.request(
            method=method,
            headers=headers,
            params=params,
            url=f"{self.cnf.base_url}/api/index.php/{endpoint}",
            json=body
        )
        if not response.ok:
            raise RequestException
        return response.json()

    def login(self) -> dict:
        """
        Authenticates the user with the credentials
        inserted from the prompt.
        """

        # Get the user credentials
        username = input("Username: ")
        password = getpass(prompt="Password: ")

        credentials = {
            "login": username,
            "password": password
        }

        return self.call(method="POST", endpoint="login", body=credentials)

    def invoices(self, params: Optional[dict] = None) -> dict:
        """
        Gets the list of invoices from dolibarr API.

        Params:
        --------------------------------------------
        params: dict -> list of filtering parameters.
        """
        return self.call(endpoint='invoices', params=params)

    def third_parties(self, params: Optional[dict] = None) -> dict:
        """
        Gets the list of third parties from dolibarr API.

        Params:
        --------------------------------------------
        params: dict -> list of filtering parameters.
        """
        return self.call(endpoint="thirdparties", params=params)
