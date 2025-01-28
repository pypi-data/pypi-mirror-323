from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SteelBoundaryConditionsDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STEEL_BOUNDARY_CONDITIONS_DEFINITION_TYPE_UNKNOWN: _ClassVar[SteelBoundaryConditionsDefinitionType]
    STEEL_BOUNDARY_CONDITIONS_DEFINITION_TYPE_2D: _ClassVar[SteelBoundaryConditionsDefinitionType]
STEEL_BOUNDARY_CONDITIONS_DEFINITION_TYPE_UNKNOWN: SteelBoundaryConditionsDefinitionType
STEEL_BOUNDARY_CONDITIONS_DEFINITION_TYPE_2D: SteelBoundaryConditionsDefinitionType

class SteelBoundaryConditions(_message.Message):
    __slots__ = ("no", "definition_type", "coordinate_system", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "intermediate_nodes", "nodal_supports", "member_hinges", "different_properties_supports", "different_properties_hinges", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_HINGES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_HINGES_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: SteelBoundaryConditionsDefinitionType
    coordinate_system: str
    user_defined_name_enabled: bool
    name: str
    comment: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    intermediate_nodes: bool
    nodal_supports: ArrayOfSteelBoundaryConditionsNodalSupports
    member_hinges: ArrayOfSteelBoundaryConditionsMemberHinges
    different_properties_supports: bool
    different_properties_hinges: bool
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[SteelBoundaryConditionsDefinitionType, str]] = ..., coordinate_system: _Optional[str] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., intermediate_nodes: bool = ..., nodal_supports: _Optional[_Union[ArrayOfSteelBoundaryConditionsNodalSupports, _Mapping]] = ..., member_hinges: _Optional[_Union[ArrayOfSteelBoundaryConditionsMemberHinges, _Mapping]] = ..., different_properties_supports: bool = ..., different_properties_hinges: bool = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfSteelBoundaryConditionsNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfSteelBoundaryConditionsMemberHinges(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
