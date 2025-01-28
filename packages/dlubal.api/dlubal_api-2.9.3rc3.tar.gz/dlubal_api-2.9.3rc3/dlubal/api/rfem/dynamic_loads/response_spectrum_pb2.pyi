from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseSpectrumDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_SPECTRUM_DEFINITION_TYPE_UNKNOWN: _ClassVar[ResponseSpectrumDefinitionType]
    RESPONSE_SPECTRUM_DEFINITION_TYPE_ACCORDING_TO_STANDARD: _ClassVar[ResponseSpectrumDefinitionType]
    RESPONSE_SPECTRUM_DEFINITION_TYPE_GENERATED_FROM_ACCELEROGRAM: _ClassVar[ResponseSpectrumDefinitionType]
    RESPONSE_SPECTRUM_DEFINITION_TYPE_USER_DEFINED: _ClassVar[ResponseSpectrumDefinitionType]

class ResponseSpectrumDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_SPECTRUM_DIRECTION_ALONG_X: _ClassVar[ResponseSpectrumDirection]
    RESPONSE_SPECTRUM_DIRECTION_ALONG_Y: _ClassVar[ResponseSpectrumDirection]
    RESPONSE_SPECTRUM_DIRECTION_ALONG_Z: _ClassVar[ResponseSpectrumDirection]
RESPONSE_SPECTRUM_DEFINITION_TYPE_UNKNOWN: ResponseSpectrumDefinitionType
RESPONSE_SPECTRUM_DEFINITION_TYPE_ACCORDING_TO_STANDARD: ResponseSpectrumDefinitionType
RESPONSE_SPECTRUM_DEFINITION_TYPE_GENERATED_FROM_ACCELEROGRAM: ResponseSpectrumDefinitionType
RESPONSE_SPECTRUM_DEFINITION_TYPE_USER_DEFINED: ResponseSpectrumDefinitionType
RESPONSE_SPECTRUM_DIRECTION_ALONG_X: ResponseSpectrumDirection
RESPONSE_SPECTRUM_DIRECTION_ALONG_Y: ResponseSpectrumDirection
RESPONSE_SPECTRUM_DIRECTION_ALONG_Z: ResponseSpectrumDirection

class ResponseSpectrum(_message.Message):
    __slots__ = ("no", "definition_type", "user_defined_name_enabled", "name", "user_defined_response_spectrum_step_enabled", "user_defined_response_spectrum_period_step", "user_defined_spectrum_sorted", "user_defined_response_spectrum", "comment", "is_generated", "generating_object_info", "damping", "min_t", "max_t", "direction", "sample_count", "accelerogram", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_STEP_ENABLED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_PERIOD_STEP_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_SPECTRUM_SORTED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_RESPONSE_SPECTRUM_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    DAMPING_FIELD_NUMBER: _ClassVar[int]
    MIN_T_FIELD_NUMBER: _ClassVar[int]
    MAX_T_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    ACCELEROGRAM_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: ResponseSpectrumDefinitionType
    user_defined_name_enabled: bool
    name: str
    user_defined_response_spectrum_step_enabled: bool
    user_defined_response_spectrum_period_step: float
    user_defined_spectrum_sorted: bool
    user_defined_response_spectrum: ArrayOfResponseSpectrumUserDefinedResponseSpectrum
    comment: str
    is_generated: bool
    generating_object_info: str
    damping: float
    min_t: float
    max_t: float
    direction: ResponseSpectrumDirection
    sample_count: int
    accelerogram: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[ResponseSpectrumDefinitionType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., user_defined_response_spectrum_step_enabled: bool = ..., user_defined_response_spectrum_period_step: _Optional[float] = ..., user_defined_spectrum_sorted: bool = ..., user_defined_response_spectrum: _Optional[_Union[ArrayOfResponseSpectrumUserDefinedResponseSpectrum, _Mapping]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., damping: _Optional[float] = ..., min_t: _Optional[float] = ..., max_t: _Optional[float] = ..., direction: _Optional[_Union[ResponseSpectrumDirection, str]] = ..., sample_count: _Optional[int] = ..., accelerogram: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfResponseSpectrumUserDefinedResponseSpectrum(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
