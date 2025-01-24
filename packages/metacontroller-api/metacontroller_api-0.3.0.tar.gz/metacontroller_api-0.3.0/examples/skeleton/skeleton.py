from metacontroller_api import DecoratorController, DecoratorSyncRequest, DecoratorSyncResponse
from metacontroller_api.contrib.flask import serve
from metacontroller_api.types import CustomizeRequest, CustomizeResponse, DecoratorFinalizeResponse


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

    def finalize(self, request: DecoratorSyncRequest) -> DecoratorFinalizeResponse:
        # ...
        return {
            "finalized": True,
            "labels": {},
            "annotations": {},
            "status": {},
            "attachments": [],
            "resyncAfterSeconds": 0,
        }


serve(MyController())
