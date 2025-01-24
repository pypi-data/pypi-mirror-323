"""
Expose a Metacontroller implementation as a Flask app.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Literal, cast

import flask

from metacontroller_api.controllers import CompositeController, DecoratorController
from metacontroller_api.types import (
    CompositeFinalizeResponse,
    CompositeSyncRequest,
    CompositeSyncResponse,
    CustomizeRequest,
    CustomizeResponse,
    DecoratorFinalizeResponse,
    DecoratorSyncRequest,
    DecoratorSyncResponse,
)


@dataclass
class RequestResponse:
    type Kind = Literal["customize", "sync", "finalize"]
    type Request = CustomizeRequest | CompositeSyncRequest | DecoratorSyncRequest
    type Response = (
        CustomizeResponse
        | CompositeFinalizeResponse
        | DecoratorFinalizeResponse
        | CompositeSyncResponse
        | DecoratorSyncResponse
        | None
    )

    kind: Kind
    request: Request
    request_time: datetime
    response: Response
    response_time: datetime
    duration_seconds: float
    exception: Exception | None


class MetacontrollerBlueprint(flask.Blueprint):
    """
    Wraps a Metacontroller implementation to expose it via an API.
    """

    def __init__(
        self,
        controller: CompositeController | DecoratorController,
        log_request_response: Callable[[RequestResponse], None] | None = None,
    ) -> None:
        super().__init__(
            name=type(controller).__name__,
            import_name=__name__,  # TODO: Can we provide a more appropriate value here?
        )

        self._log_request_response = log_request_response

        self.add_url_rule("/customize", None, self._make_dispatch("customize", controller.customize), methods=["POST"])
        self.add_url_rule("/sync", None, self._make_dispatch("sync", controller.sync), methods=["POST"])  # type: ignore[type-var]
        self.add_url_rule("/finalize", None, self._make_dispatch("finalize", controller.finalize), methods=["POST"])  # type: ignore[type-var]

    def _make_dispatch[TReq: RequestResponse.Request, TResp: RequestResponse.Response](
        self,
        kind: RequestResponse.Kind,
        request_handler: Callable[[TReq], TResp],
    ) -> Callable[[], flask.Response]:
        def handler() -> flask.Response:
            assert isinstance(flask.request.json, dict)
            request = cast(TReq, flask.request.json)
            request_time = datetime.now(timezone.utc)
            try:
                response: TResp | None = request_handler(request)
                exception: Exception | None = None
            except Exception as exc:
                response = None
                exception = exc

            if self._log_request_response:
                # NOTE: Exception in the log callback will hide previous exception.
                response_time = datetime.now(timezone.utc)
                self._log_request_response(
                    RequestResponse(
                        kind=kind,
                        request=request,
                        request_time=request_time,
                        response=response,
                        response_time=response_time,
                        duration_seconds=response_time.timestamp() - response_time.timestamp(),
                        exception=exception,
                    )
                )

            if exception is not None:
                raise exception

            return flask.jsonify(response)

        handler.__name__ = kind
        return handler


def serve(
    controller: CompositeController | DecoratorController,
    host: str | None = None,
    port: int | None = None,
    debug: bool = False,
    load_dotenv: bool = True,
    **options: Any,
) -> None:
    """
    Create a Flask app serving the given controller and runs it.
    """

    app = flask.Flask(__name__)
    app.register_blueprint(MetacontrollerBlueprint(controller))
    app.run(
        host=host,
        port=port,
        debug=debug,
        load_dotenv=load_dotenv,
        **options,
    )
