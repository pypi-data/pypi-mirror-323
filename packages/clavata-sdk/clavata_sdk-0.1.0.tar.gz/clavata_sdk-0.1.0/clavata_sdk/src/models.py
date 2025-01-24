from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast

from google.protobuf import timestamp_pb2

from .protobufs.clavata.gateway.v1 import jobs_pb2
from .protobufs.clavata.shared.v1 import shared_pb2

type JsonAny = dict[str, "JsonAny"] | list["JsonAny"] | str | int | float | bool | None
type OutcomeName = Literal["TRUE", "FALSE", "FAILED"]
type JobStatusName = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELED"]


def to_proto_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    return timestamp_pb2.Timestamp(
        seconds=int(dt.timestamp()),
        nanos=int((dt.timestamp() - int(dt.timestamp())) * 1e9),
    )


def from_proto_job_status(
    status: shared_pb2.JobStatus,
) -> JobStatusName:
    match status:
        case shared_pb2.JOB_STATUS_PENDING:
            return "PENDING"
        case shared_pb2.JOB_STATUS_RUNNING:
            return "RUNNING"
        case shared_pb2.JOB_STATUS_COMPLETED:
            return "COMPLETED"
        case shared_pb2.JOB_STATUS_FAILED:
            return "FAILED"
        case shared_pb2.JOB_STATUS_CANCELED:
            return "CANCELED"
        case _:
            raise ValueError(f"Unknown or unspecified job status: {status}")


def from_proto_outcome(outcome: shared_pb2.Outcome) -> OutcomeName:
    match outcome:
        case shared_pb2.OUTCOME_TRUE:
            return "TRUE"
        case shared_pb2.OUTCOME_FALSE:
            return "FALSE"
        case shared_pb2.OUTCOME_FAILED:
            return "FAILED"
        case _:
            raise ValueError(f"Unknown or unspecified outcome: {outcome}")


@dataclass
class ContentData:
    """
    Used to send the request data for the create_job and evaluate methods.

    ### Fields:
    - text: The text content to evaluate.
    - image: The image content to evaluate.

    #### Note:
    At present, either text or image must be provided. Not both. In the future, we will likely
    add support for both types to be included if they are logically related.
    """

    text: str | None = None
    image: bytes | None = None

    def to_proto(self) -> shared_pb2.ContentData:
        return shared_pb2.ContentData(
            text=self.text,
            image=self.image,
        )

    @staticmethod
    def from_proto(proto: shared_pb2.ContentData) -> "ContentData":
        return ContentData(
            text=proto.text,
            image=proto.image,
        )


@dataclass
class CreateJobRequest:
    """
    Used to send the request data for the create_job method.

    ### Fields:
    - content: The content to evaluate. Can be either a single ContentData object or a list of ContentData objects.
    If a single ContentData object is provided, it will be automatically converted to a list.
    - policy_id: The ID of the policy to use for content evaluation.
    - wait_for_completion: If True, the request will wait for the job to complete before returning.
    If False, the request will return immediately after the job is created and you can then use a
    GetJobRequest to check the status of the job. If a job is complete, the results will be returned
    in the response.
    """

    content: list[ContentData]
    policy_id: str
    wait_for_completion: bool

    def to_proto(self) -> jobs_pb2.CreateJobRequest:
        return jobs_pb2.CreateJobRequest(
            content_data=[content.to_proto() for content in self.content],
            policy_id=self.policy_id,
            wait_for_completion=self.wait_for_completion,
        )


@dataclass
class SectionEvaluationReport:
    name: str
    message: str
    result: OutcomeName

    @staticmethod
    def from_proto(
        proto: shared_pb2.PolicyEvaluationReport.SectionEvaluationReport,
    ) -> "SectionEvaluationReport":
        return SectionEvaluationReport(
            name=proto.name,
            message=proto.message,
            result=from_proto_outcome(proto.result),
        )


@dataclass
class PolicyEvaluationReport[T: JsonAny]:
    policy_id: str
    policy_name: str
    policy_version_id: str
    result: OutcomeName
    section_evaluation_reports: list[SectionEvaluationReport]
    content_hash: str
    content_metadata: T

    @staticmethod
    def from_proto(proto: shared_pb2.PolicyEvaluationReport) -> "PolicyEvaluationReport":
        return PolicyEvaluationReport(
            policy_id=proto.policy_id,
            policy_name=proto.policy_key,
            policy_version_id=proto.policy_version_id,
            result=from_proto_outcome(proto.result),
            section_evaluation_reports=[
                SectionEvaluationReport.from_proto(section)
                for section in proto.section_evaluation_reports
            ],
            content_hash=proto.content_hash,
            content_metadata=cast(T, proto.content_metadata),
        )


@dataclass
class JobResult:
    uuid: str
    job_uuid: str
    content_hash: str
    report: PolicyEvaluationReport
    created: datetime

    @staticmethod
    def from_proto(proto: shared_pb2.JobResult) -> "JobResult":
        return JobResult(
            uuid=proto.uuid,
            job_uuid=proto.job_uuid,
            content_hash=proto.content_hash,
            report=PolicyEvaluationReport.from_proto(proto.report),
            created=proto.created.ToDatetime(),
        )


@dataclass
class Job:
    job_uuid: str
    customer_id: str
    policy_id: str
    policy_version_id: str
    status: JobStatusName
    content_data: list[ContentData]
    results: list[JobResult]
    created: datetime
    updated: datetime
    completed: datetime

    @classmethod
    def from_proto(cls, proto: shared_pb2.Job) -> "Job":
        return Job(
            job_uuid=proto.job_uuid,
            customer_id=proto.customer_id,
            policy_id=proto.policy_id,
            policy_version_id=proto.policy_version_id,
            status=from_proto_job_status(proto.status),
            content_data=[ContentData.from_proto(content) for content in proto.content_data],
            results=[JobResult.from_proto(result) for result in proto.results],
            created=proto.created.ToDatetime(),
            updated=proto.updated.ToDatetime(),
            completed=proto.completed.ToDatetime(),
        )


@dataclass
class CreateJobResponse(Job):
    @classmethod
    def from_proto(cls, proto: jobs_pb2.CreateJobResponse) -> "CreateJobResponse":
        job = super().from_proto(proto.job)
        return CreateJobResponse(**job.__dict__)


@dataclass
class EvaluateRequest:
    """
    Used to send the request data for the evaluate method.

    ### Fields:
    - content: The content to evaluate. Can be either a single ContentData object or a list of ContentData objects.
    If a single ContentData object is provided, it will be automatically converted to a list.
    - policy_id: The ID of the policy to evaluate the content against.
    - include_evaluation_report: Whether to include the full evaluation report in the response. If False, only the result for
    the entire policy is returned
    """

    content: list[ContentData]
    policy_id: str
    include_evaluation_report: bool

    def to_proto(self) -> jobs_pb2.EvaluateRequest:
        return jobs_pb2.EvaluateRequest(
            content_data=[content.to_proto() for content in self.content],
            policy_id=self.policy_id,
            include_evaluation_report=self.include_evaluation_report,
        )


@dataclass
class EvaluateResponse:
    job_uuid: str
    content_hash: str
    policy_evaluation_report: PolicyEvaluationReport

    @staticmethod
    def from_proto(proto: jobs_pb2.EvaluateResponse) -> "EvaluateResponse":
        return EvaluateResponse(
            job_uuid=proto.job_uuid,
            content_hash=proto.content_hash,
            policy_evaluation_report=PolicyEvaluationReport.from_proto(
                proto.policy_evaluation_report
            ),
        )


@dataclass
class TimeRange:
    start: datetime
    end: datetime
    inclusive: bool

    def to_proto(self) -> shared_pb2.TimeRange:
        return shared_pb2.TimeRange(
            start=to_proto_timestamp(self.start),
            end=to_proto_timestamp(self.end),
            inclusive=self.inclusive,
        )


@dataclass
class ListJobsQuery:
    created_time_range: TimeRange
    updated_time_range: TimeRange
    completed_time_range: TimeRange
    status: JobStatusName

    def to_proto(self) -> jobs_pb2.ListJobsRequest.Query:
        return jobs_pb2.ListJobsRequest.Query(
            created_time_range=self.created_time_range.to_proto(),
            updated_time_range=self.updated_time_range.to_proto(),
            completed_time_range=self.completed_time_range.to_proto(),
            status=self.status,
        )

    def to_proto_request(self) -> jobs_pb2.ListJobsRequest:
        return jobs_pb2.ListJobsRequest(query=self.to_proto())


@dataclass
class ListJobsResponse:
    jobs: list[Job]

    @classmethod
    def from_proto(cls, proto: jobs_pb2.ListJobsResponse) -> "ListJobsResponse":
        return ListJobsResponse(jobs=[Job.from_proto(job) for job in proto.jobs])


@dataclass
class GetJobRequest:
    job_uuid: str

    def to_proto(self) -> jobs_pb2.GetJobRequest:
        return jobs_pb2.GetJobRequest(job_uuid=self.job_uuid)


@dataclass
class GetJobResponse(Job):
    @classmethod
    def from_proto(cls, proto: jobs_pb2.GetJobResponse) -> "GetJobResponse":
        job = super().from_proto(proto.job)
        return GetJobResponse(**job.__dict__)
