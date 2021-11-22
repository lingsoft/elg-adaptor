from elg.model import TextRequest, StructuredTextRequest, AudioRequest
from elg.model.request.StructuredTextRequest import Text

import time
import copy
import requests
import unittest

# Configuration
port = 8181
url = 'http://localhost:%d/process' % port
headers = {"Content-Type": "application/json; charset=utf-8"}

# Request
params = {"pipe": "smegram"}

text_content = "This is a test."
text_req = TextRequest(content=text_content, params=params)
struct_req = StructuredTextRequest(texts=[Text(content=text_content)]*2, params=params)

audio_content = open('test.wav', 'rb').read()
audio_req = AudioRequest(content=audio_content, params=params, format="LINEAR16")

request = struct_req
response_type = 'texts'


class TestELG(unittest.TestCase):

    def test_res_type(self):
        res = requests.post(url, headers=headers, json=request.dict())
        assert res is not None
        res = res.json()
        assert 'response' in res
        assert res['response']['type'] == response_type
        # print(res)

    def test_resp_time(self):
        st = time.time()
        for i in range(20):
            requests.post(url, headers=headers, json=request.dict())
        et = time.time()
        print("Average response time: %.2f"%((et-st)/20))

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
        # print(res)

    def test_lar_req(self):
        large_req = copy.deepcopy(request)
        large_text = " ".join([text_content]*10000)
        if isinstance(large_req, TextRequest):
            large_req.content = large_text
        elif isinstance(large_req, AudioRequest):
            large_audio = b"".join([audio_content]*100)
            large_req.content = large_audio
        elif isinstance(large_req, StructuredTextRequest):
            large_req.texts=[Text(content=large_text)] * 2
        res = requests.post(url, headers=headers, json=large_req.dict())
        assert res is not None
        res = res.json()
        assert 'response' or 'failure' in res

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
        # print(res)

    def test_inv_schema(self):
        request_dict = request.dict()
        request_dict.pop('type')
        res = requests.post(url, headers=headers, json=request_dict)
        assert res is not None, "The server returned None"
        res = res.json()
        assert 'failure' in res
        # print(res)



