import os

from elg.model import TextRequest, StructuredTextRequest, AudioRequest
from elg.model.request.StructuredTextRequest import Text

import json
import yaml
import time
import copy
import threading
import requests
import unittest


def load_request():
    '''
    Load configs for testing from a yaml file.
    The path of the yaml should be set as a environment variable YAML_FILE
    :return:
    '''


    # Configs
    configs = yaml.load(open(os.environ.get('YAML_FILE')), Loader=yaml.FullLoader)

    # Configuration
    port = configs['port']
    url = 'http://localhost:%d/process' % port

    # Request
    headers = {'Accept': 'application/json'}
    params = configs['params'] if 'params' in configs else None
    request_type = configs['request_type']
    response_type = configs['response_type']

    if request_type == 'text':
        content = configs['text']
        request = TextRequest(content=content, params=params)
    elif request_type == 'structuredtext':
        content = configs['text']
        request = StructuredTextRequest(texts=[Text(content=content)] * 2, params=params)
    elif request_type == 'audio':
        with open(configs['audio'], 'rb') as f:
            content = f.read()
        request = AudioRequest(content=content, format='LINEAR16')
    else:
        raise RuntimeError('request_type not support')

    if response_type not in ['annotations', 'audio', 'classification', 'texts']:
        raise RuntimeError('response_type not support')

    trial_num = configs['trial_num']
    thread_num = configs['thread_num']
    text = configs.get('text')

    return url, headers, request, params, response_type, content, text, trial_num, thread_num


def audio_req_files(req, text=None):
    '''
    Turn the AudioRequest into a file dict for requests
    :param req: AudioRequest
    '''
    content = {"type": "audio",  "format": "LINEAR16"}
    if text is not None:
        with open(text, 'r') as f:
            content["features"] = {"transcript": f.read()} 
    files = {
        "request": (
            None,
            json.dumps(content),
            "application/json",
        ),
        "content": (None, req.content, "audio/x-wav"),
    }

    return files


class TestELG(unittest.TestCase):
    url, headers, request, params, response_type, content, text, trial_num, thread_num = load_request()

    def test_res_type(self):
        """
        Validate the response type
        """
        # for audio input
        if isinstance(self.request, AudioRequest):
            res = requests.post(self.url, headers=self.headers, files=audio_req_files(self.request, self.text))
        else:
            res = requests.post(self.url, headers=self.headers, json=self.request.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' in res, 'Wrong type returns'
        assert res['response']['type'] == self.response_type
        # print(res)

    def test_resp_time(self):
        """
        Record the response time by averaging over multiple requests
        """
        times = self.trial_num
        st = time.time()
        for i in range(times):
            if isinstance(self.request, AudioRequest):
                requests.post(self.url, headers=self.headers, files=audio_req_files(self.request))
            else:
                requests.post(self.url, headers=self.headers, json=self.request.dict())
        et = time.time()
        print("Average response time: %.2fs"%((et-st)/times))

    def test_emp_req(self):
        """
        Test the service with empty request, it should return empty response or failure or error
        """
        empty_req = copy.deepcopy(self.request)
        if isinstance(empty_req, TextRequest):
            empty_req.content = ""
        elif isinstance(empty_req, AudioRequest):
            empty_req.content = b""
        elif isinstance(empty_req, StructuredTextRequest):
            empty_req.texts=[]
        if isinstance(self.request, AudioRequest):
            res = requests.post(self.url, headers=self.headers, files=audio_req_files(empty_req))
        else:
            res = requests.post(self.url, headers=self.headers, json=empty_req.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' or 'failure' or 'error' in res
        # print(res)

    def test_lar_req(self):
        '''
        Test the service with large request
        '''
        large_req = copy.deepcopy(self.request)

        if isinstance(large_req, TextRequest):
            large_text = " ".join([self.content] * 10000)
            large_req.content = large_text
        elif isinstance(large_req, AudioRequest):
            large_req.content = b"".join([self.content]*10)
        elif isinstance(large_req, StructuredTextRequest):
            large_text = " ".join([self.content] * 10000)
            large_req.texts=[Text(content=large_text)] * 2

        if isinstance(self.request, AudioRequest):
            res = requests.post(self.url, headers=self.headers, files=audio_req_files(large_req))
        else:
            res = requests.post(self.url, headers=self.headers, json=large_req.dict())
        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' or 'failure' or 'error' in res
        # print(res)

    def test_large_req_mix(self):
        """Test stuctured texts which contain mix of large and small text.
        API service should still work and also return warning on the part of texts that was failed to parse"""
        if isinstance(self.request, AudioRequest) or isinstance(self.request, TextRequest):
            return
        large_text_content = " ".join([self.content]*100)
        large_mix_req = StructuredTextRequest(texts=[Text(content=self.content)]*2 + [Text(content=large_text_content)], params=self.params)
        res = requests.post(self.url, headers=self.headers, json=large_mix_req.dict())

        assert res is not None
        assert res.status_code == 200
        res = res.json()
        assert 'response' in res
        self.assertIn(res['response']['type'], ['texts', 'annotations', 'classification'], msg='Wrong type returns')
        if res['response']['type'] == 'texts': # only tnpp and other annotation tool APIs needs
            warnings = res['response']['warnings']
            self.assertIsInstance(warnings, list, 'given object is not List type')
            assert warnings[0]['code'] == 'elg.request.too.large'

    def test_inv_param(self):
        '''
        Test the service with invalid params
        Failure or error should be returned
        If no param, this test will be skipped
        '''
        inv_req = copy.deepcopy(self.request)
        if not self.params: return
        inv_params = copy.deepcopy(self.params)
        for k in inv_params:
            inv_params[k] = 'inv'
        inv_req.params = inv_params
        if isinstance(self.request, AudioRequest):
            res = requests.post(self.url, headers=self.headers, files=audio_req_files(inv_req))
        else:
            res = requests.post(self.url, headers=self.headers, json=inv_req.dict())
        assert res is not None, "The server returned None"
        assert res.status_code == 200
        res = res.json()
        assert 'failure' or 'error' in res
        # print(res)

    def test_inv_schema(self):
        '''
        Test the service with invalid request schema
        Failure or error should be returned
        '''
        if isinstance(self.request, AudioRequest):
            inv_req = copy.deepcopy(self.request)
            request_dict = audio_req_files(inv_req)
            request_dict.pop('content')
            res = requests.post(self.url, headers=self.headers, files=request_dict)
        else:
            request_dict = self.request.dict()
            request_dict.pop('type')
            res = requests.post(self.url, headers=self.headers, json=request_dict)
        assert res is not None, "The server returned None"
        assert res.status_code == 200
        res = res.json()
        assert 'failure' or 'error' in res
        # print(res)

    def test_load(self):
        """
        Load test the service with concurrent requests
        """
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
        t_num = self.thread_num
        times = self.trial_num
        t_list = []
        for i in range(t_num):
            if isinstance(self.request, AudioRequest):
                t_list.append(ReqThread(self.url, self.headers, audio_req_files(self.request), times, True))
            else:
                t_list.append(ReqThread(self.url, self.headers, self.request.dict(), times))
            t_list[i].start()

        st = time.time()
        for t in t_list:
            t.join()
        et = time.time()
        print("Multithreading: Average response time: %.2fs"%((et-st)/(t_num*times)))
