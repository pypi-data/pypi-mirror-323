from ...shared.v1 import shared_pb2 as _shared_pb2
from ....google.api import visibility_pb2 as _visibility_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EvaluateRequest(_message.Message):
    __slots__ = ("content_data", "policy_id", "include_evaluation_report")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.ContentData]
    policy_id: str
    include_evaluation_report: bool
    def __init__(self, content_data: _Optional[_Iterable[_Union[_shared_pb2.ContentData, _Mapping]]] = ..., policy_id: _Optional[str] = ..., include_evaluation_report: bool = ...) -> None: ...

class EvaluateResponse(_message.Message):
    __slots__ = ("job_uuid", "content_hash", "policy_evaluation_report")
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_HASH_FIELD_NUMBER: _ClassVar[int]
    POLICY_EVALUATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    content_hash: str
    policy_evaluation_report: _shared_pb2.PolicyEvaluationReport
    def __init__(self, job_uuid: _Optional[str] = ..., content_hash: _Optional[str] = ..., policy_evaluation_report: _Optional[_Union[_shared_pb2.PolicyEvaluationReport, _Mapping]] = ...) -> None: ...

class CreateJobRequest(_message.Message):
    __slots__ = ("content_data", "policy_id", "wait_for_completion")
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.ContentData]
    policy_id: str
    wait_for_completion: bool
    def __init__(self, content_data: _Optional[_Iterable[_Union[_shared_pb2.ContentData, _Mapping]]] = ..., policy_id: _Optional[str] = ..., wait_for_completion: bool = ...) -> None: ...

class CreateJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: _shared_pb2.Job
    def __init__(self, job: _Optional[_Union[_shared_pb2.Job, _Mapping]] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ("job_uuid",)
    JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    job_uuid: str
    def __init__(self, job_uuid: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ("job",)
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: _shared_pb2.Job
    def __init__(self, job: _Optional[_Union[_shared_pb2.Job, _Mapping]] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ("query",)
    class Query(_message.Message):
        __slots__ = ("created_time_range", "updated_time_range", "completed_time_range", "status")
        CREATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        UPDATED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        COMPLETED_TIME_RANGE_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        created_time_range: _shared_pb2.TimeRange
        updated_time_range: _shared_pb2.TimeRange
        completed_time_range: _shared_pb2.TimeRange
        status: _shared_pb2.JobStatus
        def __init__(self, created_time_range: _Optional[_Union[_shared_pb2.TimeRange, _Mapping]] = ..., updated_time_range: _Optional[_Union[_shared_pb2.TimeRange, _Mapping]] = ..., completed_time_range: _Optional[_Union[_shared_pb2.TimeRange, _Mapping]] = ..., status: _Optional[_Union[_shared_pb2.JobStatus, str]] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: ListJobsRequest.Query
    def __init__(self, query: _Optional[_Union[ListJobsRequest.Query, _Mapping]] = ...) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_shared_pb2.Job]
    def __init__(self, jobs: _Optional[_Iterable[_Union[_shared_pb2.Job, _Mapping]]] = ...) -> None: ...
