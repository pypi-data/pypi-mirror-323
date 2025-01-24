# python-metacontroller-api

[Metacontroller]: https://github.com/metacontroller/metacontroller/

API for implementing Kubernetes controllers via [Metacontroller].

## Example

<!-- run `uvx mksync -i README.md` to update. -->
<!-- include code:python examples/skeleton/skeleton.py -->

```python
from metacontroller_api import DecoratorController, DecoratorSyncRequest, DecoratorSyncResponse
from metacontroller_api.contrib.flask import serve
from metacontroller_api.types import CustomizeRequest, CustomizeResponse, FinalizeRequest, FinalizeResponse


class MyController(DecoratorController):
    def customize(self, request: CustomizeRequest) -> CustomizeResponse:
        # ...
        return {
            "relatedResources": [],
        }

    def sync(self, request: DecoratorSyncRequest) -> DecoratorSyncResponse:
        # ...
        return {
            "labels": {},
            "annotations": {},
            "status": {},
            "attachments": [],
            "resyncAfterSeconds": 0,
        }

    def finalize(self, request: FinalizeRequest) -> FinalizeResponse:
        # ...
        return {"finalized": True}uvx mksync README.md -i


serve(MyController())
```

<!-- end include -->
