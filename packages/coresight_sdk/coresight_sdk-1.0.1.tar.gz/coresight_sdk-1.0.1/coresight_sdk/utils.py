import requests
from coresight_sdk.exceptions import ApiException

class APIRequestHandler:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

    def _handle_response(self, response: requests.Response) -> dict:
        if not response.ok:
            try:
                details = response.json()
            except Exception:
                details = {}
            raise ApiException(
                status_code=response.status_code,
                message=response.text,
                details=details
            )
        return response.json()

    def get(self, endpoint: str,params: dict = None) -> dict:
        response = requests.get(f"{self.base_url}{endpoint}",params=params, headers=self._get_headers())
        return self._handle_response(response)

    def post(self, endpoint: str, payload: dict) -> dict:
        response = requests.post(f"{self.base_url}{endpoint}", json=payload, headers=self._get_headers())
        return self._handle_response(response)

    def put(self, endpoint: str, payload: dict) -> dict:
        response = requests.put(f"{self.base_url}{endpoint}", json=payload, headers=self._get_headers())
        return self._handle_response(response)

    def delete(self, endpoint: str) -> dict:
        response = requests.delete(f"{self.base_url}{endpoint}", headers=self._get_headers())
        return self._handle_response(response)
