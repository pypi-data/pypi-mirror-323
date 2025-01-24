from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetCustomerReviewLimitRequest(_message.Message):
    __slots__ = ("customer_id",)
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    def __init__(self, customer_id: _Optional[str] = ...) -> None: ...

class GetCustomerReviewLimitResponse(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class UpdateCustomerReviewLimitRequest(_message.Message):
    __slots__ = ("customer_id", "limit")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    limit: int
    def __init__(self, customer_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class UpdateCustomerReviewLimitResponse(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...
