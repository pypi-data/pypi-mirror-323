from typing import Any, NotRequired, ReadOnly, TypedDict

# Kubernetes-native types


class OwnerReference(TypedDict):
    apiVersion: str
    kind: str
    name: str
    uid: str
    blockOwnerDeletion: NotRequired[bool]
    controller: NotRequired[bool]


class ObjectMetadata(TypedDict):
    """See https://dev-k8sref-io.web.app/docs/common-definitions/objectmeta-/."""

    name: str
    generateName: NotRequired[str | None]
    namespace: NotRequired[str]
    labels: NotRequired[dict[str, str]]
    annotations: NotRequired[dict[str, str]]

    finalizers: NotRequired[list[str]]
    managedFields: NotRequired[list[Any]]
    ownerReferences: NotRequired[list[OwnerReference]]

    creationTimestamp: ReadOnly[NotRequired[str]]
    deletionGracePeriodSeconds: ReadOnly[NotRequired[int]]
    deletionTimestamp: ReadOnly[NotRequired[str]]
    generation: ReadOnly[NotRequired[int]]
    resourceVersion: ReadOnly[NotRequired[str]]
    uid: ReadOnly[NotRequired[str]]


class Resource(TypedDict):
    apiVersion: str
    kind: str
    metadata: ObjectMetadata

    type: NotRequired[str]
    data: NotRequired[dict[str, str]]
    stringData: NotRequired[dict[str, str]]
    spec: NotRequired[dict[str, Any]]
    status: NotRequired["Status"]


type Status = dict[str, Any]
"""
Kubernetes resource status object.
"""


# Metacontroller types


type AssociativeResourceArray = dict[str, dict[str, "Resource"]]
"""
Represents an associative array used for conveniently representing a set of resources keyed by their type and name.

For example, a Pod named `my-pod` in the `my-namespace` namespace could be accessed as follows if the parent is
also in `my-namespace`:

    array["Pod.v1"]["my-pod"]

Alternatively, if the parent resource is cluster scoped, the Pod could be accessed as:

    array["Pod.v1"]["my-namespace/my-pod"]
"""


class ResourceRule(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/customize.html#customize-hook-response."""

    apiVersion: str
    """
    The API `<group>/<version>` of the parent resource, or just <version> for core APIs. (e.g. `v1`,
    `apps/v1`, `batch/v1`).
    """

    resource: str
    """
    The canonical, lowercase, plural name of the parent resource. (e.g. `deployments`,
    `replicasets`, `statefulsets`).
    """

    labelSelector: NotRequired[dict[str, str]]
    """ A `v1.LabelSelector` object. Omit if not used (i.e. Namespace or Names should be used). """

    namespace: NotRequired[str]
    """ Optional. The Namespace to select in. """

    names: NotRequired[list[str]]
    """ Optional. A list of strings, representing individual objects to return. """


class CustomizeRequest(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/customize.html#customize-hook-request."""

    controller: Resource
    """
    The whole CompositeController object, like what you might get from
    `kubectl get compositecontroller <name> -o json`.
    """

    parent: Resource
    """ The parent object, like what you might get from `kubectl get <parent-resource> <parent-name> -o json`. """


class CustomizeResponse(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/customize.html#customize-hook-response."""

    relatedResources: list["ResourceRule"]
    """ A list of JSON objects (ResourceRules) representing all the desired related resource descriptions. """


class DecoratorSyncRequest(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/decoratorcontroller.html#sync-hook-request."""

    controller: Resource
    """ The whole DecoratorController object, like what you might get from
    `kubectl get decoratorcontroller <name> -o json`. """

    object: Resource
    """ The target object, like what you might get from `kubectl get <target-resource> <target-name> -o json`. """

    attachments: AssociativeResourceArray
    """ An associative array of attachments that already exist. """

    related: AssociativeResourceArray
    """ An associative array of related objects that exists, if customize hook was specified. See the customize hook """

    finalizing: bool
    """ This is always false for the sync hook. See the finalize hook for details. """


class DecoratorSyncResponse(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/decoratorcontroller.html#sync-hook-response."""

    labels: dict[str, str]
    """ A map of key-value pairs for labels to set on the target object. """

    annotations: dict[str, str]
    """ A map of key-value pairs for annotations to set on the target object. """

    status: NotRequired[Status | None]
    """ A JSON object that will completely replace the status field within the target object. Leave unspecified
    or null to avoid changing status. """

    attachments: list[Resource]
    """ A list of JSON objects representing all the desired attachments for this target object. """

    resyncAfterSeconds: float
    """ Set the delay (in seconds, as a float) before an optional, one-time, per-object resync. """


class DecoratorFinalizeResponse(DecoratorSyncResponse):
    """
    See https://metacontroller.github.io/metacontroller/api/decoratorcontroller.html#finalize-hook-response.
    """

    finalized: bool
    """ A boolean indicating whether you are done finalizing. """


class CompositeSyncRequest(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/compositecontroller.html#sync-hook-request."""

    controller: Resource
    """
    The whole CompositeController object, like what you might get from
    `kubectl get compositecontroller <name> -o json`.
    """

    parent: Resource
    """ The parent object, like what you might get from `kubectl get <parent-resource> <parent-name> -o json`. """

    children: AssociativeResourceArray
    """ An associative array of child objects that already exist. """

    related: AssociativeResourceArray
    """ An associative array of related objects that exists, if customize hook was specified. See the customize hook """

    finalizing: bool
    """ This is always false for the sync hook. See the finalize hook for details. """


class CompositeSyncResponse(TypedDict):
    """See https://metacontroller.github.io/metacontroller/api/compositecontroller.html#sync-hook-response."""

    status: Status | None
    """
    A JSON object that will completely replace the status field within the parent object.

    What you put in status is up to you, but usually it's best to follow conventions established by controllers
    like Deployment. You should compute status based only on the children that existed when your hook was called;
    status represents a report on the last observed state, not the new desired state.
    """

    children: list[Resource]
    """ A list of JSON objects representing all the desired children for this parent object. """

    resyncAfterSeconds: float
    """ Set the delay (in seconds, as a float) before an optional, one-time, per-object resync. """


class CompositeFinalizeResponse(CompositeSyncResponse):
    """
    See https://metacontroller.github.io/metacontroller/api/compositecontroller.html#finalize-hook-response.
    """

    finalized: bool
    """ A boolean indicating whether you are done finalizing. """


class Factories:
    # We can't define functions on the TypeDict subclass, nor override __new__. So we need to provide
    # alternative methods for conveniently constructing payloads.

    @staticmethod
    def DecoratorSyncResponse(
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        status: Status | None = None,
        attachments: list[Resource] | None = None,
        resyncAfterSeconds: int = 0,
    ) -> "DecoratorSyncResponse":
        return {
            "labels": labels or {},
            "annotations": annotations or {},
            "status": status,
            "attachments": attachments or [],
            "resyncAfterSeconds": resyncAfterSeconds,
        }

    @staticmethod
    def DecoratorFinalizeResponse(
        finalized: bool,
        labels: dict[str, str] | None = None,
        annotations: dict[str, str] | None = None,
        status: Status | None = None,
        attachments: list[Resource] | None = None,
        resyncAfterSeconds: int = 0,
    ) -> "DecoratorFinalizeResponse":
        return {
            "finalized": finalized,
            "labels": labels or {},
            "annotations": annotations or {},
            "status": status,
            "attachments": attachments or [],
            "resyncAfterSeconds": resyncAfterSeconds,
        }

    @staticmethod
    def CompositeSyncResponse(
        status: Status,
        children: list[Resource],
        resyncAfterSeconds: float = 0,
    ) -> "CompositeSyncResponse":
        return {
            "status": status,
            "children": children or [],
            "resyncAfterSeconds": resyncAfterSeconds,
        }

    @staticmethod
    def CompositeFinalizeResponse(
        finalized: bool,
        status: Status,
        children: list[Resource],
        resyncAfterSeconds: float = 0,
    ) -> "CompositeFinalizeResponse":
        return {
            "finalized": finalized,
            "status": status,
            "children": children or [],
            "resyncAfterSeconds": resyncAfterSeconds,
        }
