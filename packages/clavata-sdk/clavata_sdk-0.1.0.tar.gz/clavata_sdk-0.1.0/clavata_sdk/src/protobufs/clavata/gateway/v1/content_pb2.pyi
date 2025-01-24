from ...shared.v1 import shared_pb2 as _shared_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddToCustomerContentRequest(_message.Message):
    __slots__ = ("content_data",)
    CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    content_data: _containers.RepeatedCompositeFieldContainer[_shared_pb2.ContentData]
    def __init__(self, content_data: _Optional[_Iterable[_Union[_shared_pb2.ContentData, _Mapping]]] = ...) -> None: ...

class AddToCustomerContentResponse(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetCustomerContentRequest(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetCustomerContentResponse(_message.Message):
    __slots__ = ("contents",)
    class ExtendedContentData(_message.Message):
        __slots__ = ("customer_content_id", "content_data")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        CONTENT_DATA_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        content_data: _shared_pb2.ContentData
        def __init__(self, customer_content_id: _Optional[str] = ..., content_data: _Optional[_Union[_shared_pb2.ContentData, _Mapping]] = ...) -> None: ...
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    contents: _containers.RepeatedCompositeFieldContainer[GetCustomerContentResponse.ExtendedContentData]
    def __init__(self, contents: _Optional[_Iterable[_Union[GetCustomerContentResponse.ExtendedContentData, _Mapping]]] = ...) -> None: ...

class DeleteFromCustomerContentRequest(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteFromCustomerContentResponse(_message.Message):
    __slots__ = ("customer_content_ids", "conflicts")
    class DatasetConflictValue(_message.Message):
        __slots__ = ("dataset_id", "name")
        DATASET_ID_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        dataset_id: str
        name: str
        def __init__(self, dataset_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...
    class DatasetConflict(_message.Message):
        __slots__ = ("customer_content_id", "datasets")
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        DATASETS_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        datasets: _containers.RepeatedCompositeFieldContainer[DeleteFromCustomerContentResponse.DatasetConflictValue]
        def __init__(self, customer_content_id: _Optional[str] = ..., datasets: _Optional[_Iterable[_Union[DeleteFromCustomerContentResponse.DatasetConflictValue, _Mapping]]] = ...) -> None: ...
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    conflicts: _containers.RepeatedCompositeFieldContainer[DeleteFromCustomerContentResponse.DatasetConflict]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ..., conflicts: _Optional[_Iterable[_Union[DeleteFromCustomerContentResponse.DatasetConflict, _Mapping]]] = ...) -> None: ...

class UpdateCustomerContentsRequest(_message.Message):
    __slots__ = ("updates",)
    class Body(_message.Message):
        __slots__ = ("customer_content_id", "update")
        class Update(_message.Message):
            __slots__ = ("update_mask", "title", "text", "labels")
            UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
            TITLE_FIELD_NUMBER: _ClassVar[int]
            TEXT_FIELD_NUMBER: _ClassVar[int]
            LABELS_FIELD_NUMBER: _ClassVar[int]
            update_mask: _field_mask_pb2.FieldMask
            title: str
            text: str
            labels: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...
        CUSTOMER_CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
        UPDATE_FIELD_NUMBER: _ClassVar[int]
        customer_content_id: str
        update: UpdateCustomerContentsRequest.Body.Update
        def __init__(self, customer_content_id: _Optional[str] = ..., update: _Optional[_Union[UpdateCustomerContentsRequest.Body.Update, _Mapping]] = ...) -> None: ...
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    updates: _containers.RepeatedCompositeFieldContainer[UpdateCustomerContentsRequest.Body]
    def __init__(self, updates: _Optional[_Iterable[_Union[UpdateCustomerContentsRequest.Body, _Mapping]]] = ...) -> None: ...

class UpdateCustomerContentsResponse(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ListCustomerContentRequest(_message.Message):
    __slots__ = ("query",)
    class Query(_message.Message):
        __slots__ = ("labels", "content_modality")
        LABELS_FIELD_NUMBER: _ClassVar[int]
        CONTENT_MODALITY_FIELD_NUMBER: _ClassVar[int]
        labels: _containers.RepeatedScalarFieldContainer[str]
        content_modality: _shared_pb2.ContentModality
        def __init__(self, labels: _Optional[_Iterable[str]] = ..., content_modality: _Optional[_Union[_shared_pb2.ContentModality, str]] = ...) -> None: ...
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: ListCustomerContentRequest.Query
    def __init__(self, query: _Optional[_Union[ListCustomerContentRequest.Query, _Mapping]] = ...) -> None: ...

class ListCustomerContentResponse(_message.Message):
    __slots__ = ("customer_content_ids",)
    CUSTOMER_CONTENT_IDS_FIELD_NUMBER: _ClassVar[int]
    customer_content_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, customer_content_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ListCustomerContentLabelsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCustomerContentLabelsResponse(_message.Message):
    __slots__ = ("labels",)
    LABELS_FIELD_NUMBER: _ClassVar[int]
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, labels: _Optional[_Iterable[str]] = ...) -> None: ...
