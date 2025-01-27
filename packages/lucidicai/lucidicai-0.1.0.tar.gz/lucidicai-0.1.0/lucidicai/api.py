import requests

class LucidicAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Api-Key {self.api_key}"}
        self.base_url = "https://dashboard.lucidic.ai/demo/api/v1"
        self.endpoints = {
            "verifyAPIKey": "/testendpoint",
        }
    def verifyAPIKey(self, testprompt="Tell me a joke"):
        url = f'{self.base_url}/{self.endpoints["verifyAPIKey"]}'
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={
                    'prompt': testprompt,
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            print(f"Error during API Call: {e}")
            raise