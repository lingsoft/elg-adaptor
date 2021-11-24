from elg.model import TextRequest, StructuredTextRequest, AudioRequest
from elg.model.request.StructuredTextRequest import Text
from elg.model import response

import json
import time
import copy
import threading
import requests
import unittest

# Configuration
port = 8080
url = 'http://localhost:%d/process'%port
headers = {'Accept': 'application/json'}

# Request
params = None

text_content = "Idag släpper KB språkmodeller."
text_req = TextRequest(content=text_content, params=params)
struct_req = StructuredTextRequest(texts=[Text(content=text_content)]*2, params=params)

audio_content = open('test.wav', 'rb').read()
audio_req = {
    "request": (
        None,
        json.dumps(
            {
                "type": "audio",
                "format": "LINEAR16",
            }
        ),
        "application/json",
    ),
    "content": (None, audio_content, "audio/x-wav"),
}

# Specify your request and response type
request = audio_req
resp_typs = ['annotations', 'audio', 'classification', 'texts']
response_type = 'annotations'


class TestELG(unittest.TestCase):

    def test_res_type(self):
        # for audio input
        if isinstance(request, dict):
            res = requests.post(url, headers=headers, files=request)
        else:
            res = requests.post(url, headers=headers, json=request.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' in res
        assert res['response']['type'] == response_type
        # print(res)

    def test_resp_time(self):
        st = time.time()
        for i in range(10):
            if isinstance(request, dict):
                requests.post(url, headers=headers, files=request)
            else:
                requests.post(url, headers=headers, json=request.dict())
        et = time.time()
        print("Average response time: %.2fs"%((et-st)/10))

    def test_emp_req(self):
        empty_req = copy.deepcopy(request)
        if isinstance(empty_req, TextRequest):
            empty_req.content = ""
        elif isinstance(empty_req, dict):
            empty_req['content'] = (None, b"", "audio/x-wav")
        elif isinstance(empty_req, StructuredTextRequest):
            empty_req.texts=[]
        if isinstance(request, dict):
            res = requests.post(url, headers=headers, files=empty_req)
        else:
            res = requests.post(url, headers=headers, json=empty_req.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' or 'failure' or 'error' in res
        # print(res)

    def test_lar_req(self):
        large_req = copy.deepcopy(request)
        large_text = " ".join([text_content]*10000)
        if isinstance(large_req, TextRequest):
            large_req.content = large_text
        elif isinstance(large_req, dict):
            large_audio = b"".join([audio_content]*100)
            large_req['content'] = (None, large_audio, "audio/x-wav")
        elif isinstance(large_req, StructuredTextRequest):
            large_req.texts=[Text(content=large_text)] * 2
        if isinstance(request, dict):
            res = requests.post(url, headers=headers, files=large_req)
        else:
            res = requests.post(url, headers=headers, json=large_req.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' or 'failure' or 'error' in res
        print(res)

    def test_inv_param(self):
        inv_req = copy.deepcopy(request)
        if not params: return
        inv_params = copy.deepcopy(params)
        for k in inv_params:
            inv_params[k] = 'inv'
        inv_req.params = inv_params
        if isinstance(request, dict):
            res = requests.post(url, headers=headers, files=inv_req)
        else:
            res = requests.post(url, headers=headers, json=inv_req.dict())
        assert res is not None, "The server returned None"
        assert res.status_code == 200
        res = res.json()
        assert 'failure' or 'error' in res
        # print(res)

    def test_inv_schema(self):
        if isinstance(request, dict):
            inv_req = copy.deepcopy(request)
            inv_req.pop('content')
            res = requests.post(url, headers=headers, files=inv_req)
        else:
            request_dict = request.dict()
            request_dict.pop('type')
            res = requests.post(url, headers=headers, json=request_dict)
        assert res is not None, "The server returned None"
        assert res.status_code == 200
        res = res.json()
        assert 'failure' or 'error' in res
        # print(res)

    def test_load(self):
        class ReqThread(threading.Thread):
            def __init__(self, url, headers, data, times, audios=False):
                super().__init__()
                self.url = url
                self.headers = headers
                self.data = data
                self.times = times
                self.audios = audios

            def run(self) -> None:
                for i in range(self.times):
                    if self.audios:
                        requests.post(self.url, headers=self.headers, files=self.data)
                    else:
                        requests.post(self.url, headers=self.headers, json=self.data)
        t_num = 10
        times = 10
        t_list = []
        for i in range(t_num):
            if isinstance(request, dict):
                t_list.append(ReqThread(url, headers, request, times, True))
            else:
                t_list.append(ReqThread(url, headers, request.dict(), times))
            t_list[i].start()

        st = time.time()
        for t in t_list:
            t.join()
        et = time.time()
        print("Average response time: %.2fs"%((et-st)/(t_num*times)))