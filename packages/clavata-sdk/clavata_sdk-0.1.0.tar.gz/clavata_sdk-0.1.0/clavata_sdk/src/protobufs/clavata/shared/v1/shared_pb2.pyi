from ....google.api import visibility_pb2 as _visibility_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContentModality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[ContentModality]
    TEXT: _ClassVar[ContentModality]
    IMAGE: _ClassVar[ContentModality]
    AUDIO: _ClassVar[ContentModality]
    VIDEO: _ClassVar[ContentModality]

class QueryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUERY_TYPE_UNSPECIFIED: _ClassVar[QueryType]
    QUERY_TYPE_OBJECT: _ClassVar[QueryType]
    QUERY_TYPE_CONCEPT: _ClassVar[QueryType]
    QUERY_TYPE_CONTEXT: _ClassVar[QueryType]
    QUERY_TYPE_QUESTION: _ClassVar[QueryType]
    QUERY_TYPE_EXACT: _ClassVar[QueryType]
    QUERY_TYPE_FUZZY: _ClassVar[QueryType]
    QUERY_TYPE_SENTIMENT: _ClassVar[QueryType]

class Outcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTCOME_UNSPECIFIED: _ClassVar[Outcome]
    OUTCOME_FALSE: _ClassVar[Outcome]
    OUTCOME_TRUE: _ClassVar[Outcome]
    OUTCOME_FAILED: _ClassVar[Outcome]

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATUS_UNSPECIFIED: _ClassVar[JobStatus]
    JOB_STATUS_PENDING: _ClassVar[JobStatus]
    JOB_STATUS_RUNNING: _ClassVar[JobStatus]
    JOB_STATUS_COMPLETED: _ClassVar[JobStatus]
    JOB_STATUS_FAILED: _ClassVar[JobStatus]
    JOB_STATUS_CANCELED: _ClassVar[JobStatus]

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    CLAVATA_ADMIN: _ClassVar[Role]
    ACCOUNT_ADMIN: _ClassVar[Role]
    POLICY_WRITER: _ClassVar[Role]
    API_USER: _ClassVar[Role]

class Scopes(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCOPE_UNSPECIFIED: _ClassVar[Scopes]
    CLIENT_ACCESS: _ClassVar[Scopes]
    API_ACCESS: _ClassVar[Scopes]

class SortOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_ORDER_UNSPECIFIED: _ClassVar[SortOrder]
    SORT_ORDER_ASC: _ClassVar[SortOrder]
    SORT_ORDER_DESC: _ClassVar[SortOrder]
UNSPECIFIED: ContentModality
TEXT: ContentModality
IMAGE: ContentModality
AUDIO: ContentModality
VIDEO: ContentModality
QUERY_TYPE_UNSPECIFIED: QueryType
QUERY_TYPE_OBJECT: QueryType
QUERY_TYPE_CONCEPT: QueryType
QUERY_TYPE_CONTEXT: QueryType
QUERY_TYPE_QUESTION: QueryType
QUERY_TYPE_EXACT: QueryType
QUERY_TYPE_FUZZY: QueryType
QUERY_TYPE_SENTIMENT: QueryType
OUTCOME_UNSPECIFIED: Outcome
OUTCOME_FALSE: Outcome
OUTCOME_TRUE: Outcome
OUTCOME_FAILED: Outcome
JOB_STATUS_UNSPECIFIED: JobStatus
JOB_STATUS_PENDING: JobStatus
JOB_STATUS_RUNNING: JobStatus
JOB_STATUS_COMPLETED: JobStatus
JOB_STATUS_FAILED: JobStatus
JOB_STATUS_CANCELED: JobStatus
ROLE_UNSPECIFIED: Role
CLAVATA_ADMIN: Role
ACCOUNT_ADMIN: Role
POLICY_WRITER: Role
API_USER: Role
SCOPE_UNSPECIFIED: Scopes
CLIENT_ACCESS: Scopes
API_ACCESS: Scopes
SORT_ORDER_UNSPECIFIED: SortOrder
SORT_ORDER_ASC: SortOrder
SORT_ORDER_DESC: SortOrder

class ContentData(_message.Message):
    __slots__ = ("content_hash", "text", "image", "image_url", "video_url", "audio_url", "labels", "content_type", "metadata", "title")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    VIDEO_URL_FIELD_NUMBER: _ClassVar[int]
    AUDIO_URL_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    text: str
    image: bytes
    image_url: str
    video_url: str
    audio_url: str
    labels: _containers.RepeatedScalarFieldContainer[str]
    content_type: str
    metadata: _struct_pb2.Value
    title: str
    def __init__(self, content_hash: _Optional[str] = ..., text: _Optional[str] = ..., image: _Optional[bytes] = ..., image_url: _Optional[str] = ..., video_url: _Optional[str] = ..., audio_url: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ..., content_type: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., title: _Optional[str] = ...) -> None: ...

class CompilationError(_message.Message):
    __slots__ = ("message", "line", "column")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    message: str
    line: int
    column: int
    def __init__(self, message: _Optional[str] = ..., line: _Optional[int] = ..., column: _Optional[int] = ...) -> None: ...

class QueryBody(_message.Message):
    __slots__ = ("query_type", "query", "context_details", "query_id")
    class QueryContext(_message.Message):
        __slots__ = ("context_relation", "target_label")
        CONTEXT_RELATION_FIELD_NUMBER: _ClassVar[int]
        TARGET_LABEL_FIELD_NUMBER: _ClassVar[int]
        context_relation: str
        target_label: str
        def __init__(self, context_relation: _Optional[str] = ..., target_label: _Optional[str] = ...) -> None: ...
    QUERY_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_DETAILS_FIELD_NUMBER: _ClassVar[int]
    QUERY_ID_FIELD_NUMBER: _ClassVar[int]
    query_type: QueryType
    query: str
    context_details: QueryBody.QueryContext
    query_id: str
    def __init__(self, query_type: _Optional[_Union[QueryType, str]] = ..., query: _Optional[str] = ..., context_details: _Optional[_Union[QueryBody.QueryContext, _Mapping]] = ..., query_id: _Optional[str] = ...) -> None: ...

class QueryResultBody(_message.Message):
    __slots__ = ("answer", "confidence")
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    answer: bool
    confidence: float
    def __init__(self, answer: bool = ..., confidence: _Optional[float] = ...) -> None: ...

class SourceRange(_message.Message):
    __slots__ = ("start", "end")
    class SourceLocation(_message.Message):
        __slots__ = ("line", "column")
        LINE_FIELD_NUMBER: _ClassVar[int]
        COLUMN_FIELD_NUMBER: _ClassVar[int]
        line: int
        column: int
        def __init__(self, line: _Optional[int] = ..., column: _Optional[int] = ...) -> None: ...
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    start: SourceRange.SourceLocation
    end: SourceRange.SourceLocation
    def __init__(self, start: _Optional[_Union[SourceRange.SourceLocation, _Mapping]] = ..., end: _Optional[_Union[SourceRange.SourceLocation, _Mapping]] = ...) -> None: ...

class PolicyEvaluationReport(_message.Message):
    __slots__ = ("policy_id", "policy_key", "policy_version_id", "name", "result", "section_evaluation_reports", "exception_evaluation_report", "content_hash", "content_metadata")
    class AssertionEvaluationReport(_message.Message):
        __slots__ = ("result", "message", "source_range")
        RESULT_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        result: Outcome
        message: str
        source_range: SourceRange
        def __init__(self, result: _Optional[_Union[Outcome, str]] = ..., message: _Optional[str] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ...) -> None: ...
    class ExceptionEvaluationReport(_message.Message):
        __slots__ = ("result", "assertion_evaluation_reports", "source_range")
        RESULT_FIELD_NUMBER: _ClassVar[int]
        ASSERTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        result: Outcome
        assertion_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.AssertionEvaluationReport]
        source_range: SourceRange
        def __init__(self, result: _Optional[_Union[Outcome, str]] = ..., assertion_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.AssertionEvaluationReport, _Mapping]]] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ...) -> None: ...
    class SectionEvaluationReport(_message.Message):
        __slots__ = ("name", "result", "message", "assertion_evaluation_reports", "exception_evaluation_report", "source_range")
        NAME_FIELD_NUMBER: _ClassVar[int]
        RESULT_FIELD_NUMBER: _ClassVar[int]
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        ASSERTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
        EXCEPTION_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
        SOURCE_RANGE_FIELD_NUMBER: _ClassVar[int]
        name: str
        result: Outcome
        message: str
        assertion_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.AssertionEvaluationReport]
        exception_evaluation_report: PolicyEvaluationReport.ExceptionEvaluationReport
        source_range: SourceRange
        def __init__(self, name: _Optional[str] = ..., result: _Optional[_Union[Outcome, str]] = ..., message: _Optional[str] = ..., assertion_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.AssertionEvaluationReport, _Mapping]]] = ..., exception_evaluation_report: _Optional[_Union[PolicyEvaluationReport.ExceptionEvaluationReport, _Mapping]] = ..., source_range: _Optional[_Union[SourceRange, _Mapping]] = ...) -> None: ...
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SECTION_EVALUATION_REPORTS_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    CONTENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    policy_version_id: str
    name: str
    result: Outcome
    section_evaluation_reports: _containers.RepeatedCompositeFieldContainer[PolicyEvaluationReport.SectionEvaluationReport]
    exception_evaluation_report: PolicyEvaluationReport.ExceptionEvaluationReport
    content_hash: str
    content_metadata: _struct_pb2.Value
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., name: _Optional[str] = ..., result: _Optional[_Union[Outcome, str]] = ..., section_evaluation_reports: _Optional[_Iterable[_Union[PolicyEvaluationReport.SectionEvaluationReport, _Mapping]]] = ..., exception_evaluation_report: _Optional[_Union[PolicyEvaluationReport.ExceptionEvaluationReport, _Mapping]] = ..., content_hash: _Optional[str] = ..., content_metadata: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class TimeRange(_message.Message):
    __slots__ = ("start", "end", "inclusive")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    INCLUSIVE_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    inclusive: bool
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., inclusive: bool = ...) -> None: ...

class Policy(_message.Message):
    __slots__ = ("customer_id", "policy_id", "policy_key", "active_version_id", "created", "updated", "expunged", "disabled")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    policy_id: str
    policy_key: str
    active_version_id: str
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    expunged: bool
    disabled: bool
    def __init__(self, customer_id: _Optional[str] = ..., policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., active_version_id: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expunged: bool = ..., disabled: bool = ...) -> None: ...

class PolicyVersion(_message.Message):
    __slots__ = ("policy_identifier", "version_id", "policy_text", "policy_blob", "expunged", "metadata", "created")
    POLICY_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_TEXT_FIELD_NUMBER: _ClassVar[int]
    POLICY_BLOB_FIELD_NUMBER: _ClassVar[int]
    EXPUNGED_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    policy_identifier: PolicyIdentifier
    version_id: str
    policy_text: str
    policy_blob: bytes
    expunged: bool
    metadata: bytes
    created: _timestamp_pb2.Timestamp
    def __init__(self, policy_identifier: _Optional[_Union[PolicyIdentifier, _Mapping]] = ..., version_id: _Optional[str] = ..., policy_text: _Optional[str] = ..., policy_blob: _Optional[bytes] = ..., expunged: bool = ..., metadata: _Optional[bytes] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PolicyIdentifier(_message.Message):
    __slots__ = ("policy_id", "policy_key")
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    policy_key: str
    def __init__(self, policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ...) -> None: ...

class JobResult(_message.Message):
    __slots__ = ("uuid", "job_uuid", "content_hash", "report", "created")
    UUID_FIELD_NUMBER: _ClassVar[int]
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    job_uuid: str
    content_hash: str
    report: PolicyEvaluationReport
    created: _timestamp_pb2.Timestamp
    def __init__(self, uuid: _Optional[str] = ..., job_uuid: _Optional[str] = ..., content_hash: _Optional[str] = ..., report: _Optional[_Union[PolicyEvaluationReport, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Job(_message.Message):
    __slots__ = ("job_uuid", "customer_id", "status", "metadata", "content_data", "results", "created", "updated", "completed", "policy_id", "policy_version_id", "policy_draft_id")
    class Metadata(_message.Message):
        __slots__ = ("customer_id",)
        CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
        customer_id: str
        def __init__(self, customer_id: _Optional[str] = ...) -> None: ...
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_DRAFT_ID_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    customer_id: str
    status: JobStatus
    metadata: Job.Metadata
    content_data: _containers.RepeatedCompositeFieldContainer[ContentData]
    results: _containers.RepeatedCompositeFieldContainer[JobResult]
    created: _timestamp_pb2.Timestamp
    updated: _timestamp_pb2.Timestamp
    completed: _timestamp_pb2.Timestamp
    policy_id: str
    policy_version_id: str
    policy_draft_id: str
    def __init__(self, job_uuid: _Optional[str] = ..., customer_id: _Optional[str] = ..., status: _Optional[_Union[JobStatus, str]] = ..., metadata: _Optional[_Union[Job.Metadata, _Mapping]] = ..., content_data: _Optional[_Iterable[_Union[ContentData, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[JobResult, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., completed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., policy_id: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., policy_draft_id: _Optional[str] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ("token", "expiration", "valid", "customer_uuid", "scopes", "user_email", "role", "first_name", "last_name", "user_id")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_UUID_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    USER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    token: str
    expiration: _timestamp_pb2.Timestamp
    valid: bool
    customer_uuid: str
    scopes: _containers.RepeatedScalarFieldContainer[Scopes]
    user_email: str
    role: Role
    first_name: str
    last_name: str
    user_id: str
    def __init__(self, token: _Optional[str] = ..., expiration: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., valid: bool = ..., customer_uuid: _Optional[str] = ..., scopes: _Optional[_Iterable[_Union[Scopes, str]]] = ..., user_email: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...
