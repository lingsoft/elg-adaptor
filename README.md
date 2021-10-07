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

For test cases, you need to give the configurations and some request parameters.

The tester will test text request and structured text request. 

After starting you elg service, use the following script to run the test
```shell
python -m unittest elg_tester.py
```
 
