from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrecheckFailureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRECHECK_FAILURE_TYPE_UNSPECIFIED: _ClassVar[PrecheckFailureType]
    PRECHECK_FAILURE_TYPE_NCMEC: _ClassVar[PrecheckFailureType]
PRECHECK_FAILURE_TYPE_UNSPECIFIED: PrecheckFailureType
PRECHECK_FAILURE_TYPE_NCMEC: PrecheckFailureType

class PrecheckFailure(_message.Message):
    __slots__ = ("type", "message", "details")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    type: PrecheckFailureType
    message: str
    details: _struct_pb2.Value
    def __init__(self, type: _Optional[_Union[PrecheckFailureType, str]] = ..., message: _Optional[str] = ..., details: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
