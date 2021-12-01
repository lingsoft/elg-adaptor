## Introduction
Custom failure classes and general tester to support ELG Python SDK


### Failure Classes

All the failure codes and related messages are in the [elg-messages_en.properties](elg-messages_en.properties)

Here in the [elg_adaptor.py](elg_adaptor.py), 
only `RequestInvalid`, `RequestTooLarge`, and `InternalError` have been defined.

An example using one of the error as response in a ELG service could be like:

```python
from elg.model import Failure
from elg_adaptor import InternalError
try:
    service = lambda x: x+1
    service("1")
except Exception as err:
    failure = Failure(errors=[
        InternalError(str(err)).as_status()
    ])
```

### Test Cases

To test the ELG service, you can specify some configurations in a yaml file. 
There are two samples under the [test_configs](test_configs) folder.
```yaml
port:  # port of the service
params: # should be a dict, empty if no params
request_type: # type of request, select one from 'text', 'structuredtext', 'audio'
audio: # path to the audio file, if request_type is 'audio'
text: # text of the request, if request_type is 'text' or 'structuredtext'
response_type: # type of response, select one from 'annotations', 'audio', 'classification', 'texts'
trial_num: # for testing the response time
thread_num: # for testing the response time
```

Set the path to the yaml file as a environment variable
```shell
export YAML_FILE=<path-to-yaml>
```

After starting you elg service, use the following script to run the test
```shell
python -m unittest elg_tester.py
```
 
