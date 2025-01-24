import asyncio
from collections.abc import AsyncIterator, Awaitable
import os
from typing import Callable, Concatenate

import grpc
from grpc import aio as grpc_aio
from grpc.aio import Metadata

from .protobufs.clavata.gateway.v1 import gateway_pb2_grpc, jobs_pb2
from .models import (
    CreateJobRequest,
    CreateJobResponse,
    EvaluateRequest,
    EvaluateResponse,
    GetJobRequest,
    GetJobResponse,
    ListJobsQuery,
    ListJobsResponse,
)

# FIXME(@boichee): Let's make sure to add debug level logging so customers using our SDK can see
# relevant information.


class ClavataClient:
    """
    The ClavataClient class provides a convienient way to interact with the Clavata API.

    It provides methods for creating jobs, evaluating content, and retrieving jobs.

    A Clavata API key is required to use the SDK. You can either provide an API key to the constructor with
    the `auth_token` parameter, or set the `CLAVATA_API_KEY` environment variable. Note that if both
    are provided, the constructor value will take precedence.
    """

    _channel: grpc_aio.Channel | None = None
    _stub: gateway_pb2_grpc.GatewayServiceStub
    address: str
    _auth_token: str

    def __init__(self, *, host: str, port: int, auth_token: str | None = None):
        auth_token = auth_token or os.environ.get("CLAVATA_API_KEY")
        if not auth_token:
            raise ValueError(
                "No auth token provided. Please provide an auth token or set the CLAVATA_API_KEY environment variable."
            )

        self.address = f"{host}:{port}"
        self._auth_token = auth_token

    async def connect(self):
        """Establishes the gRPC channel and creates the service stub"""

        if self._channel:
            return

        # Create secure channel with default credentials (AWS certs are trusted)
        self._channel = grpc_aio.secure_channel(self.address, grpc.ssl_channel_credentials())
        self._stub = gateway_pb2_grpc.GatewayServiceStub(self._channel)

    async def close(self):
        """Closes the gRPC channel"""
        if not self._channel:
            return
        await self._channel.close()
        self._channel = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # We won't handle any exceptions here, so they will propogate
        # and will need to be handled by the caller
        await self.close()

    async def _unary_invoke[
        T, R
    ](
        self,
        method: Callable[Concatenate[T, ...], Awaitable[R]],
        request: T,
        timeout: float | None = None,
    ) -> R:
        """
        Invokes a method with the given request and timeout. This helper provides us with a way
        to handle injecting the metadata and timeout into the call. We can also add any common error
        handling here in the future.
        """
        await self.connect()
        return await method(request, metadata=self._metadata, timeout=timeout)

    async def create_job(
        self, *, request: CreateJobRequest, timeout: float | None = None
    ) -> CreateJobResponse:
        """
        Create a new content evaluation job. A job will evaluate N pieces of content against a single
        policy. The "create_job" method is "synchronous", meaning that the request will block until
        all N pieces of content have been evaluated. The results for all N pieces of content are then
        returned in the response.

        Typical usage is as follows:

        ```python
        async with ClavataClient(host="localhost", port=50051, auth_token="...") as client:
            response = await client.create_job(request=CreateJobRequest(
                policy="...",
                content=[
                    ContentData(text="..."),
                    ContentData(text="..."),
                ],
            ))
        ```

        If you only have a single piece of content to evaluate, you can pass in a single ContentData
        object instead of a list. Like so:

        ```python
        async with ClavataClient(host="localhost", port=50051, auth_token="...") as client:
            response = await client.create_job(request=CreateJobRequest(
                policy="...",
                content=ContentData(text="..."),
            ))
        ```
        """
        return await self._unary_invoke(self._stub.CreateJob, request, timeout=timeout)

    async def evaluate(
        self,
        *,
        request: EvaluateRequest,
        message_timeout: float | None = None,
        stream_timeout: float | None = None,
    ) -> AsyncIterator[EvaluateResponse]:
        """
        Evaluate N pieces of content against a single policy. One message will be sent over the
        stream for each piece of content.

        Pass an EvaluateRequest object to this method. You can construct an EvaluateRequest object
        like so:

        ```python
        request = EvaluateRequest(
            content=[ContentData(text="..."), ContentData(text="...")],
            policy_id="...",
            include_evaluation_report=True,
        )
        ```

        If you only have a single piece of content to evaluate, you can pass in a single ContentData
        object instead of a list. Like so:

        ```python
        request = EvaluateRequest(
            content=ContentData(text="..."),
            policy_id="...",
            include_evaluation_report=True,
        )
        ```

        The result of calling this method is an async iterator. As such, you can use it in an async
        for loop, or with asyncio.wait. The most common way to use this is to do:

        ```python async for response in client.evaluate(request):
            print(response)
        ```

        If, for some reason, you need finer grained control, you can manually await each message as
        it arrives from the iterator. Like so:

        ```python aiter = client.evaluate(request) while True:
            try:
                response = await anext(aiter) print(response)
            except StopAsyncIteration:
                break
        ```

        ### Timeouts:

        The evaluate method supports two types of timeouts.

        - `message_timeout`: This sets a max time between messages arriving. In this case, set
          `stream_timeout` to None. (We recommend setting this to 10 seconds initially and tuning as
          needed.)
        - `stream_timeout`: This sets a max time for the entire stream. In this case, set
          `message_timeout` to None.
        """
        await self.connect()

        try:
            stream: grpc_aio.UnaryStreamCall[
                jobs_pb2.EvaluateRequest, jobs_pb2.EvaluateResponse
            ] = self._stub.Evaluate(request, metadata=self._metadata, timeout=stream_timeout)

            # TODO(@boichee): Could at some point write a wrapper to handle the difference
            # between None and a float value more elegantly.
            if message_timeout is None:
                async for response in stream:
                    yield EvaluateResponse.from_proto(response)
            else:
                async with asyncio.timeout(message_timeout) as tm:
                    async for response in stream:
                        new_deadline = asyncio.get_running_loop().time() + message_timeout
                        tm.reschedule(new_deadline)
                        yield EvaluateResponse.from_proto(response)

        except TimeoutError:
            stream.cancel()
            raise

    async def list_jobs(
        self, *, request: ListJobsQuery, timeout: float | None = None
    ) -> ListJobsResponse:
        """
        List all jobs for the current user.
        """
        return await self._unary_invoke(self._stub.ListJobs, request, timeout=timeout)

    async def get_job(
        self, *, request: GetJobRequest, timeout: float | None = None
    ) -> GetJobResponse:
        """
        Get a single job using its UUID. If the job is not complete, the status will still be returned.
        """
        return await self._unary_invoke(self._stub.GetJob, request, timeout=timeout)

    @property
    def _metadata(self) -> Metadata:
        """Creates metadata with authorization token"""
        return Metadata(("Authorization", f"Bearer {self._auth_token}"))
