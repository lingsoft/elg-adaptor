import json
from elg.model import StatusMessage


def parse_properties(props_path):
    props = {}
    with open(props_path, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            if "=" not in line or line.startswith("#"): continue
            k, v = line.split("=", 1)
            props[k] = v
    return props


props_path = 'elg-messages_en.properties'
props = parse_properties(props_path)


class RequestInvalid:

    def __init__(self, detail=""):
        code = 'elg.request.invalid'
        self.data = {
            "code": code,
            "text": props[code],
            "params": [],
            'detail': {"msg":detail}
        }

    def as_status(self):
        return StatusMessage(**self.data)


class RequestTooLarge:

    def __init__(self, detail=""):
        code = 'elg.request.too.large'
        self.data = {
                'code':code,
                'params': [],
                'text': props[code],
                'detail': {"msg":detail}
        }

    def as_status(self):
        return StatusMessage(**self.data)
