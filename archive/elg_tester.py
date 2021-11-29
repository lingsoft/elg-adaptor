from elg.model import TextRequest, StructuredTextRequest
from elg.model.request.StructuredTextRequest import Text
import requests
import unittest

# Configuration
port = 3000
url = 'http://localhost:%d/process' % port
headers = {"Content-Type": "application/json; charset=utf-8"}

# Request
request_content = "Prošeatadoarjagat"
params = None
wrong_params = None


class TestELG(unittest.TestCase):

    def test_text_request(self):
        text_request_case = TextRequest(content=request_content, params=params).dict()
        print(requests.post(url, headers=headers, json=text_request_case).json())

    def test_long_text_request(self):
        request_too_large_failure = TextRequest(content=' '.join([request_content] * 110), params=params).dict()
        print(requests.post(url, headers=headers, json=request_too_large_failure).json())

    def test_wrong_params(self):
        request_params_wrong_failure = TextRequest(content=request_content, params=wrong_params).dict()
        print(requests.post(url, headers=headers, json=request_params_wrong_failure).json())

    def test_structured_text_request(self):
        texts_request_case = StructuredTextRequest(
            texts=[
                Text(content=request_content),
                Text(content=request_content)
            ], params=params
        ).dict()
        print(requests.post(url, headers=headers, json=texts_request_case).json())

    def test_long_structured_text_request(self):
        long_texts_request_case = StructuredTextRequest(
            texts=[
                Text(content=request_content),
                Text(content=' '.join([request_content] * 110))
            ], params=params
        ).dict()
        print(requests.post(url, headers=headers, json=long_texts_request_case).json())

    def test_structured_wrong_params(self):
        texts_wrong_params_request_case = StructuredTextRequest(
            texts=[
                Text(content=request_content),
                Text(content=request_content)
            ], params=wrong_params
        ).dict()
        print(requests.post(url, headers=headers, json=texts_wrong_params_request_case).json())



