from abc import ABC, abstractmethod

from .types import (
    CompositeFinalizeResponse,
    CompositeSyncRequest,
    CompositeSyncResponse,
    CustomizeRequest,
    CustomizeResponse,
    DecoratorFinalizeResponse,
    DecoratorSyncRequest,
    DecoratorSyncResponse,
)


class DecoratorController(ABC):
    type SyncRequest = DecoratorSyncRequest
    type SyncResponse = DecoratorSyncResponse

    def customize(self, request: CustomizeRequest) -> CustomizeResponse:
        raise NotImplementedError

    @abstractmethod
    def sync(self, request: SyncRequest) -> SyncResponse:
        raise NotImplementedError

    def finalize(self, request: SyncRequest) -> DecoratorFinalizeResponse:
        raise NotImplementedError


class CompositeController(ABC):
    type SyncRequest = CompositeSyncRequest
    type SyncResponse = CompositeSyncResponse

    def customize(self, request: CustomizeRequest) -> CustomizeResponse:
        raise NotImplementedError

    @abstractmethod
    def sync(self, request: SyncRequest) -> SyncResponse:
        raise NotImplementedError

    def finalize(self, request: SyncRequest) -> CompositeFinalizeResponse:
        raise NotImplementedError
