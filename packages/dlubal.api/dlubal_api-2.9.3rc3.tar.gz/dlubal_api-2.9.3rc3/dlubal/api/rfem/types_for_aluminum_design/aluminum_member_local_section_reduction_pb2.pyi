from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AluminumMemberLocalSectionReduction(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "components", "is_generated", "generating_object_info", "comment", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    components: ArrayOfAluminumMemberLocalSectionReductionComponents
    is_generated: bool
    generating_object_info: str
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., components: _Optional[_Union[ArrayOfAluminumMemberLocalSectionReductionComponents, _Mapping]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfAluminumMemberLocalSectionReductionComponents(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
