from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ActionCombinationCombinationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTION_COMBINATION_COMBINATION_TYPE_GENERAL: _ClassVar[ActionCombinationCombinationType]
    ACTION_COMBINATION_COMBINATION_TYPE_ENVELOPE_PERMANENT: _ClassVar[ActionCombinationCombinationType]
    ACTION_COMBINATION_COMBINATION_TYPE_ENVELOPE_TRANSIENT: _ClassVar[ActionCombinationCombinationType]
    ACTION_COMBINATION_COMBINATION_TYPE_SUPERPOSITION: _ClassVar[ActionCombinationCombinationType]
ACTION_COMBINATION_COMBINATION_TYPE_GENERAL: ActionCombinationCombinationType
ACTION_COMBINATION_COMBINATION_TYPE_ENVELOPE_PERMANENT: ActionCombinationCombinationType
ACTION_COMBINATION_COMBINATION_TYPE_ENVELOPE_TRANSIENT: ActionCombinationCombinationType
ACTION_COMBINATION_COMBINATION_TYPE_SUPERPOSITION: ActionCombinationCombinationType

class ActionCombination(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "attribute_always_editable", "comment", "design_situation", "items", "active", "construction_stage", "combination_type", "generated_load_combinations", "generated_result_combinations", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ALWAYS_EDITABLE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_LOAD_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATED_RESULT_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    attribute_always_editable: str
    comment: str
    design_situation: int
    items: ArrayOfActionCombinationItems
    active: bool
    construction_stage: int
    combination_type: ActionCombinationCombinationType
    generated_load_combinations: _containers.RepeatedScalarFieldContainer[int]
    generated_result_combinations: _containers.RepeatedScalarFieldContainer[int]
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., attribute_always_editable: _Optional[str] = ..., comment: _Optional[str] = ..., design_situation: _Optional[int] = ..., items: _Optional[_Union[ArrayOfActionCombinationItems, _Mapping]] = ..., active: bool = ..., construction_stage: _Optional[int] = ..., combination_type: _Optional[_Union[ActionCombinationCombinationType, str]] = ..., generated_load_combinations: _Optional[_Iterable[int]] = ..., generated_result_combinations: _Optional[_Iterable[int]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfActionCombinationItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
