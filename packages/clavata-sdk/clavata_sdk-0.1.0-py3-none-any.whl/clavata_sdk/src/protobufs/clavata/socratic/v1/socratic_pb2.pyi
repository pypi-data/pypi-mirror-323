from ...shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EvaluateRequest(_message.Message):
    __slots__ = ("content_data", "policy", "job_id")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    content_data: _shared_pb2.ContentData
    policy: CompiledPolicyVersion
    job_id: str
    def __init__(self, content_data: _Optional[_Union[_shared_pb2.ContentData, _Mapping]] = ..., policy: _Optional[_Union[CompiledPolicyVersion, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class EvaluateStreamRequest(_message.Message):
    __slots__ = ("content_data", "policies", "job_id")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.ContentData]
    policies: _containers.RepeatedCompositeFieldContainer[CompiledPolicyVersion]
    job_id: str
    def __init__(self, content_data: _Optional[_Iterable[_Union[_shared_pb2.ContentData, _Mapping]]] = ..., policies: _Optional[_Iterable[_Union[CompiledPolicyVersion, _Mapping]]] = ..., job_id: _Optional[str] = ...) -> None: ...

class EvaluateResponseBody(_message.Message):
    __slots__ = ("content_hash", "policy_id", "policy_key", "policy_version_id", "result", "policy_evaluation_report")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    POLICY_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    policy_id: str
    policy_key: str
    policy_version_id: str
    result: _shared_pb2.Outcome
    policy_evaluation_report: _shared_pb2.PolicyEvaluationReport
    def __init__(self, content_hash: _Optional[str] = ..., policy_id: _Optional[str] = ..., policy_key: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., result: _Optional[_Union[_shared_pb2.Outcome, str]] = ..., policy_evaluation_report: _Optional[_Union[_shared_pb2.PolicyEvaluationReport, _Mapping]] = ...) -> None: ...

class EvaluateResponse(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: EvaluateResponseBody
    def __init__(self, body: _Optional[_Union[EvaluateResponseBody, _Mapping]] = ...) -> None: ...

class EvaluateStreamResponse(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: EvaluateResponseBody
    def __init__(self, body: _Optional[_Union[EvaluateResponseBody, _Mapping]] = ...) -> None: ...

class CompiledPolicyVersion(_message.Message):
    __slots__ = ("id", "version_id", "key", "success", "policy_blob", "error")
    ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    POLICY_BLOB_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    version_id: str
    key: str
    success: bool
    policy_blob: bytes
    error: _shared_pb2.CompilationError
    def __init__(self, id: _Optional[str] = ..., version_id: _Optional[str] = ..., key: _Optional[str] = ..., success: bool = ..., policy_blob: _Optional[bytes] = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ...) -> None: ...

class CompileVersionRequest(_message.Message):
    __slots__ = ("policy_key", "policy_version_id", "policy_version_text")
    POLICY_KEY_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_TEXT_FIELD_NUMBER: _ClassVar[int]
    policy_key: str
    policy_version_id: str
    policy_version_text: str
    def __init__(self, policy_key: _Optional[str] = ..., policy_version_id: _Optional[str] = ..., policy_version_text: _Optional[str] = ...) -> None: ...

class CompileVersionResponse(_message.Message):
    __slots__ = ("compiled_version",)
    COMPILED_VERSION_FIELD_NUMBER: _ClassVar[int]
    compiled_version: CompiledPolicyVersion
    def __init__(self, compiled_version: _Optional[_Union[CompiledPolicyVersion, _Mapping]] = ...) -> None: ...

class PolicyDraftLintRequest(_message.Message):
    __slots__ = ("policy_code",)
    POLICY_CODE_FIELD_NUMBER: _ClassVar[int]
    policy_code: str
    def __init__(self, policy_code: _Optional[str] = ...) -> None: ...

class PolicyDraftLintResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: _shared_pb2.CompilationError
    def __init__(self, success: bool = ..., error: _Optional[_Union[_shared_pb2.CompilationError, _Mapping]] = ...) -> None: ...

class PolicyDraftTestRequest(_message.Message):
    __slots__ = ("test_id", "policy_code", "content_data")
    TEST_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_CODE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    test_id: str
    policy_code: str
    content_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.ContentData]
    def __init__(self, test_id: _Optional[str] = ..., policy_code: _Optional[str] = ..., content_data: _Optional[_Iterable[_Union[_shared_pb2.ContentData, _Mapping]]] = ...) -> None: ...

class PolicyDraftTestResponse(_message.Message):
    __slots__ = ("content_hash", "outcome", "policy_evaluation_report", "content_metadata")
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    POLICY_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_METADATA_FIELD_NUMBER: _ClassVar[int]
    content_hash: str
    outcome: _shared_pb2.Outcome
    policy_evaluation_report: _shared_pb2.PolicyEvaluationReport
    content_metadata: _struct_pb2.Value
    def __init__(self, content_hash: _Optional[str] = ..., outcome: _Optional[_Union[_shared_pb2.Outcome, str]] = ..., policy_evaluation_report: _Optional[_Union[_shared_pb2.PolicyEvaluationReport, _Mapping]] = ..., content_metadata: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
