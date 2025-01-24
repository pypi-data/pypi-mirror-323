from ...shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_TYPE_UNSPECIFIED: _ClassVar[ErrorType]
    ERROR_TYPE_NO_EXTRACTOR_RESPONSES: _ClassVar[ErrorType]
    ERROR_TYPE_NO_POLICY_LABELS: _ClassVar[ErrorType]
    ERROR_TYPE_LABELS_NOT_SAVED: _ClassVar[ErrorType]
    ERROR_TYPE_CONTENT_ID_NOT_FOUND: _ClassVar[ErrorType]
    ERROR_TYPE_BAD_CONTENT_ID: _ClassVar[ErrorType]
    ERROR_TYPE_MALFORMED_QUERY: _ClassVar[ErrorType]
ERROR_TYPE_UNSPECIFIED: ErrorType
ERROR_TYPE_NO_EXTRACTOR_RESPONSES: ErrorType
ERROR_TYPE_NO_POLICY_LABELS: ErrorType
ERROR_TYPE_LABELS_NOT_SAVED: ErrorType
ERROR_TYPE_CONTENT_ID_NOT_FOUND: ErrorType
ERROR_TYPE_BAD_CONTENT_ID: ErrorType
ERROR_TYPE_MALFORMED_QUERY: ErrorType

class DispatchQueryRequestBody(_message.Message):
    __slots__ = ("content_data", "query_data")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
    content_data: _shared_pb2.ContentData
    query_data: _shared_pb2.QueryBody
    def __init__(self, content_data: _Optional[_Union[_shared_pb2.ContentData, _Mapping]] = ..., query_data: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ...) -> None: ...

class DispatchQueryResponseBody(_message.Message):
    __slots__ = ("content_hash", "answer", "score", "query_data")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    answer: bool
    score: float
    query_data: _shared_pb2.QueryBody
    def __init__(self, content_hash: _Optional[str] = ..., answer: bool = ..., score: _Optional[float] = ..., query_data: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ...) -> None: ...

class DispatchQueryRequest(_message.Message):
    __slots__ = ("body", "job_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    body: DispatchQueryRequestBody
    job_id: str
    def __init__(self, body: _Optional[_Union[DispatchQueryRequestBody, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class DispatchQueryResponse(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: DispatchQueryResponseBody
    def __init__(self, body: _Optional[_Union[DispatchQueryResponseBody, _Mapping]] = ...) -> None: ...

class DispatchQueryStreamRequest(_message.Message):
    __slots__ = ("body", "job_id")
    BODY_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    body: DispatchQueryRequestBody
    job_id: str
    def __init__(self, body: _Optional[_Union[DispatchQueryRequestBody, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class DispatchQueryStreamResponse(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: DispatchQueryResponseBody
    def __init__(self, body: _Optional[_Union[DispatchQueryResponseBody, _Mapping]] = ...) -> None: ...

class DispatchQueryBatchRequest(_message.Message):
    __slots__ = ("content_data", "query_data", "threshold", "use_examine")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    USE_EXAMINE_FIELD_NUMBER: _ClassVar[int]
    content_data: _shared_pb2.ContentData
    query_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.QueryBody]
    threshold: float
    use_examine: bool
    def __init__(self, content_data: _Optional[_Union[_shared_pb2.ContentData, _Mapping]] = ..., query_data: _Optional[_Iterable[_Union[_shared_pb2.QueryBody, _Mapping]]] = ..., threshold: _Optional[float] = ..., use_examine: bool = ...) -> None: ...

class DispatchQueryBatchResponse(_message.Message):
    __slots__ = ("results",)
    class Body(_message.Message):
        __slots__ = ("content_hash", "outcome", "score", "query_data", "query_id")
        CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
        OUTCOME_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        QUERY_DATA_FIELD_NUMBER: _ClassVar[int]
        QUERY_ID_FIELD_NUMBER: _ClassVar[int]
        content_hash: str
        outcome: _shared_pb2.Outcome
        score: float
        query_data: _shared_pb2.QueryBody
        query_id: str
        def __init__(self, content_hash: _Optional[str] = ..., outcome: _Optional[_Union[_shared_pb2.Outcome, str]] = ..., score: _Optional[float] = ..., query_data: _Optional[_Union[_shared_pb2.QueryBody, _Mapping]] = ..., query_id: _Optional[str] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[DispatchQueryBatchResponse.Body]
    def __init__(self, results: _Optional[_Iterable[_Union[DispatchQueryBatchResponse.Body, _Mapping]]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("message", "error_type")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    message: str
    error_type: ErrorType
    def __init__(self, message: _Optional[str] = ..., error_type: _Optional[_Union[ErrorType, str]] = ...) -> None: ...
