from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RelationshipBetweenLoadCases(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "inclusive_load_cases", "exclusive_load_cases", "comment", "assigned_to", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INCLUSIVE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    EXCLUSIVE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    inclusive_load_cases: ArrayOfRelationshipBetweenLoadCasesInclusiveLoadCases
    exclusive_load_cases: ArrayOfRelationshipBetweenLoadCasesExclusiveLoadCases
    comment: str
    assigned_to: _containers.RepeatedScalarFieldContainer[int]
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., inclusive_load_cases: _Optional[_Union[ArrayOfRelationshipBetweenLoadCasesInclusiveLoadCases, _Mapping]] = ..., exclusive_load_cases: _Optional[_Union[ArrayOfRelationshipBetweenLoadCasesExclusiveLoadCases, _Mapping]] = ..., comment: _Optional[str] = ..., assigned_to: _Optional[_Iterable[int]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfRelationshipBetweenLoadCasesInclusiveLoadCases(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfRelationshipBetweenLoadCasesExclusiveLoadCases(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
