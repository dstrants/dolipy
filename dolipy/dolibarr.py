from getpass import getpass
from typing import Optional

import dotenv
import requests
from requests.exceptions import RequestException

from dolipy.config import DoliConfig


class DolibarrClient:
    def __init__(self, api_key: Optional[str] = None, prompt: bool = False, cache: bool = False) -> None:
        self.cnf: DoliConfig = DoliConfig()
        self.prompt: bool = prompt
        self.cache: bool = cache
        self.api_key: str = api_key or self._authenticate()

    @staticmethod
    def _cache_api_key(api_key: str) -> None:
        env_file = dotenv.find_dotenv()
        dotenv.set_key(env_file, "API_KEY", api_key)

    def _authenticate(self) -> str:
        if api_key := self.cnf.api_key:
            return api_key
        if not self.prompt:
            raise ValueError("Please provide an API Key or set prompt to True")

        resp = self.login()

        api_key = resp['success']['token']

        if self.cache:
            self._cache_api_key(api_key=api_key)

        return resp['success']['token']

    def call(self, method: str = "GET", endpoint: str = '', body: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        if not body:
            body = {}

        headers = {}
        if not endpoint == 'login':
            headers = {
                'DOLAPIKEY': self.api_key
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
        username = input("Username: ")
        password = getpass(prompt="Password: ")

        credentials = {
            "login": username,
            "password": password
        }

        return self.call(method="POST", endpoint="login", body=credentials)

    def invoices(self, params: Optional[dict] = None):
        return self.call(endpoint='invoices', params=params)