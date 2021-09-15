import json


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


class Failure:

    def __init__(self, errors):
        self.errors = []

    def add_msg(self, code, text, params, detail):
        assert code in props
        msg_dict = {
            "code":code,
            "text": text,
            "params": params,
            "detail": detail
        }
        self.errors.append(msg_dict)

    def as_json(self):
        return json.dumps({"failure":{"errors": self.errors}})


class Response:

    def __init__(self, type):
        type_list = ['classification', 'text', 'annotations', 'audio']
        assert type in type_list
        self.type = type
        self.warnings = []

    def add_msg(self, code, text, params, detail):
        assert code in props
        msg_dict = {
            "code":code,
            "text": text,
            "params": params,
            "detail": detail
        }
        self.warnings.append(msg_dict)


class AnnotationsResponse(Response):

    def __init__(self, type, features={}):
        super(AnnotationsResponse, self).__init__(type)
        assert type == 'annotations'
        self.annotations = {}
        self.features = features

    def add_annotations(self, anno_type, res):
        self.annotations[anno_type] = res

    def as_json(self):
        return json.dumps({"response":
                               {"type": self.type,
                                "warnings":self.warnings,
                                "features": self.features,
                                "annotations":self.annotations}})


class ClassificationResponse(Response):

    def __init__(self, type, classes):
        super(ClassificationResponse, self).__init__(type)
        assert type == 'classification'
        self.classes = classes

    def as_json(self):
        return json.dumps({"response":
                               {"type": self.type,
                                "warnings":self.warnings,
                                "classes":self.classes}})


class TextResponse(Response):

    def __init__(self, type, texts):
        super(TextResponse, self).__init__(type)
        assert type == 'texts'
        self.texts = texts

    def as_json(self):
        return json.dumps({"response":
                               {"type": self.type,
                                "warnings":self.warnings,
                                "texts":self.texts}})


class AudioResponse(Response):

    def __init__(self, type, content):
        super(AudioResponse, self).__init__(type)
        assert type == 'audio'
        # base64 encoded audio
        self.content = content
        self.annotations = {}

    def add_annotations(self, anno_type, res):
        self.annotations[anno_type] = res

    def as_json(self):
        return json.dumps({"response":
                               {"type": self.type,
                                "warnings": self.warnings,
                                "format": "string",
                                "annotations": self.annotations,
                                "content": self.content}})




