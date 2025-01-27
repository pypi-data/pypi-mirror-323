import pytest
from lucidicai.api import LucidicAPI

def test_verify_api_key(mocker):
    mocker.patch("requests.get", return_value=mocker.Mock(status_code=200, json=lambda: {"response": 'lmao'}))
    
    apiWrapper = LucidicAPI(api_key="dummy_api_key")
    response = apiWrapper.verifyAPIKey("test-endpoint")
    
    assert response