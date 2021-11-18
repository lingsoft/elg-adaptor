from elg.model import TextRequest, StructuredTextRequest, AudioRequest
from elg.model import TextsResponse, AnnotationsResponse, ClassificationResponse, AudioResponse
from elg.model.request.StructuredTextRequest import Text

import json
import copy
import requests
import unittest

# Configuration
port = 8181
url = 'http://localhost:%d/process' % port
headers = {"Content-Type": "application/json; charset=utf-8"}

# Request
params = {"pipe": "smegram"}

text_req = TextRequest(content="This is a test", params=params)
struct_req = StructuredTextRequest(texts=[Text(content='This is a text.')]*2, params=params)
audio_req = None


request = struct_req
response_type = 'texts'


class TestELG(unittest.TestCase):

    def test_res_type(self):
        res = requests.post(url, headers=headers, json=request.dict())
        assert res is not None
        res = res.json()
        assert 'response' in res
        assert res['response']['type'] == response_type
        print(res)

    def test_emp_req(self):
        empty_req = copy.deepcopy(request)
        if isinstance(empty_req, TextRequest):
            empty_req.content = ""
        elif isinstance(empty_req, AudioRequest):
            empty_req.content = b""
        elif isinstance(empty_req, StructuredTextRequest):
            empty_req.texts=[]

        res = requests.post(url, headers=headers, json=empty_req.dict())
        assert res is not None
        res = res.json()
        assert 'response' or 'failure' in res
        print(res)

    def val_lar_req_test(self):
        res = requests.post(url, headers=headers, json=request.dict()).json()

    def test_inv_param(self):
        inv_req = copy.deepcopy(request)
        inv_params = copy.deepcopy(params)
        for k in inv_params:
            inv_params[k] = 'inv'
        inv_req.params = inv_params

        res = requests.post(url, headers=headers, json=inv_req.dict())
        assert res is not None, "The server returned None"
        res = res.json()
        assert 'failure' in res
        print(res)

    def inv_req_schema_test(self):
        res = requests.post(url, headers=headers, json=request.dict()).json()

    def load_test(self):
        res = requests.post(url, headers=headers, json=request.dict()).json()



