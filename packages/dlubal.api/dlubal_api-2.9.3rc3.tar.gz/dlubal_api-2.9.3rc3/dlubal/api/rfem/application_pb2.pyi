from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.common import table_data_pb2 as _table_data_pb2
from dlubal.api.rfem.results import results_query_pb2 as _results_query_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApplicationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPLICATION_UNSPECIFIED: _ClassVar[ApplicationType]
    APPLICATION_DLUBAL_CENTER: _ClassVar[ApplicationType]
    APPLICATION_REPORT_VIEWER: _ClassVar[ApplicationType]
    APPLICATION_RFEM: _ClassVar[ApplicationType]
    APPLICATION_RSTAB: _ClassVar[ApplicationType]
    APPLICATION_RSECTION: _ClassVar[ApplicationType]
    APPLICATION_WEB_SECTIONS: _ClassVar[ApplicationType]
    APPLICATION_CRASH_REPORTER: _ClassVar[ApplicationType]
APPLICATION_UNSPECIFIED: ApplicationType
APPLICATION_DLUBAL_CENTER: ApplicationType
APPLICATION_REPORT_VIEWER: ApplicationType
APPLICATION_RFEM: ApplicationType
APPLICATION_RSTAB: ApplicationType
APPLICATION_RSECTION: ApplicationType
APPLICATION_WEB_SECTIONS: ApplicationType
APPLICATION_CRASH_REPORTER: ApplicationType

class CreateModelRequest(_message.Message):
    __slots__ = ("name", "template_path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    template_path: str
    def __init__(self, name: _Optional[str] = ..., template_path: _Optional[str] = ...) -> None: ...

class OpenModelRequest(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class SaveModelAsRequest(_message.Message):
    __slots__ = ("model_id", "path")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    path: str
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., path: _Optional[str] = ...) -> None: ...

class CloseModelRequest(_message.Message):
    __slots__ = ("model_id", "save_changes")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    SAVE_CHANGES_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    save_changes: bool
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., save_changes: bool = ...) -> None: ...

class CloseAllModelsRequest(_message.Message):
    __slots__ = ("save_changes",)
    SAVE_CHANGES_FIELD_NUMBER: _ClassVar[int]
    save_changes: bool
    def __init__(self, save_changes: bool = ...) -> None: ...

class ModelInfo(_message.Message):
    __slots__ = ("name", "id", "path")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: str
    path: str
    def __init__(self, name: _Optional[str] = ..., id: _Optional[str] = ..., path: _Optional[str] = ...) -> None: ...

class ModelList(_message.Message):
    __slots__ = ("model_info",)
    MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    model_info: _containers.RepeatedCompositeFieldContainer[ModelInfo]
    def __init__(self, model_info: _Optional[_Iterable[_Union[ModelInfo, _Mapping]]] = ...) -> None: ...

class ApplicationInfo(_message.Message):
    __slots__ = ("name", "type", "is_server_instance", "version", "full_version", "options", "language_name", "language_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_SERVER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FULL_VERSION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: ApplicationType
    is_server_instance: bool
    version: str
    full_version: str
    options: str
    language_name: str
    language_id: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[ApplicationType, str]] = ..., is_server_instance: bool = ..., version: _Optional[str] = ..., full_version: _Optional[str] = ..., options: _Optional[str] = ..., language_name: _Optional[str] = ..., language_id: _Optional[str] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ("object", "model_id")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    object: _any_pb2.Any
    model_id: _model_id_pb2.ModelId
    def __init__(self, object: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class ObjectList(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[Object]
    def __init__(self, objects: _Optional[_Iterable[_Union[Object, _Mapping]]] = ...) -> None: ...

class CalculateAllRequest(_message.Message):
    __slots__ = ("skip_warnings", "model_id")
    SKIP_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    skip_warnings: bool
    model_id: _model_id_pb2.ModelId
    def __init__(self, skip_warnings: bool = ..., model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ...) -> None: ...

class OperationResult(_message.Message):
    __slots__ = ("succeeded", "data", "message")
    SUCCEEDED_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    succeeded: bool
    data: str
    message: str
    def __init__(self, succeeded: bool = ..., data: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
