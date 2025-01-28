from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultCombinationCombinationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_COMBINATION_COMBINATION_TYPE_GENERAL: _ClassVar[ResultCombinationCombinationType]
    RESULT_COMBINATION_COMBINATION_TYPE_ENVELOPE_PERMANENT: _ClassVar[ResultCombinationCombinationType]
    RESULT_COMBINATION_COMBINATION_TYPE_ENVELOPE_TRANSIENT: _ClassVar[ResultCombinationCombinationType]
    RESULT_COMBINATION_COMBINATION_TYPE_SUPERPOSITION: _ClassVar[ResultCombinationCombinationType]

class ResultCombinationSrssExtremeValueSign(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_POSITIVE_OR_NEGATIVE: _ClassVar[ResultCombinationSrssExtremeValueSign]
    RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_ACCORDING_TO_LC_OR_CO: _ClassVar[ResultCombinationSrssExtremeValueSign]
    RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_NEGATIVE: _ClassVar[ResultCombinationSrssExtremeValueSign]
    RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_POSITIVE: _ClassVar[ResultCombinationSrssExtremeValueSign]
RESULT_COMBINATION_COMBINATION_TYPE_GENERAL: ResultCombinationCombinationType
RESULT_COMBINATION_COMBINATION_TYPE_ENVELOPE_PERMANENT: ResultCombinationCombinationType
RESULT_COMBINATION_COMBINATION_TYPE_ENVELOPE_TRANSIENT: ResultCombinationCombinationType
RESULT_COMBINATION_COMBINATION_TYPE_SUPERPOSITION: ResultCombinationCombinationType
RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_POSITIVE_OR_NEGATIVE: ResultCombinationSrssExtremeValueSign
RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_ACCORDING_TO_LC_OR_CO: ResultCombinationSrssExtremeValueSign
RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_NEGATIVE: ResultCombinationSrssExtremeValueSign
RESULT_COMBINATION_SRSS_EXTREME_VALUE_SIGN_POSITIVE: ResultCombinationSrssExtremeValueSign

class ResultCombination(_message.Message):
    __slots__ = ("no", "design_situation", "user_defined_name_enabled", "name", "to_solve", "comment", "combination_type", "srss_combination", "srss_extreme_value_sign", "srss_use_equivalent_linear_combination", "srss_according_load_case_or_combination", "items", "generate_subcombinations", "load_duration", "is_generated", "consider_construction_stage", "consider_construction_stage_active", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TO_SOLVE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COMBINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SRSS_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    SRSS_EXTREME_VALUE_SIGN_FIELD_NUMBER: _ClassVar[int]
    SRSS_USE_EQUIVALENT_LINEAR_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    SRSS_ACCORDING_LOAD_CASE_OR_COMBINATION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    GENERATE_SUBCOMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    LOAD_DURATION_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_CONSTRUCTION_STAGE_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    design_situation: int
    user_defined_name_enabled: bool
    name: str
    to_solve: bool
    comment: str
    combination_type: ResultCombinationCombinationType
    srss_combination: bool
    srss_extreme_value_sign: ResultCombinationSrssExtremeValueSign
    srss_use_equivalent_linear_combination: bool
    srss_according_load_case_or_combination: int
    items: ArrayOfResultCombinationItems
    generate_subcombinations: bool
    load_duration: str
    is_generated: bool
    consider_construction_stage: int
    consider_construction_stage_active: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., design_situation: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., to_solve: bool = ..., comment: _Optional[str] = ..., combination_type: _Optional[_Union[ResultCombinationCombinationType, str]] = ..., srss_combination: bool = ..., srss_extreme_value_sign: _Optional[_Union[ResultCombinationSrssExtremeValueSign, str]] = ..., srss_use_equivalent_linear_combination: bool = ..., srss_according_load_case_or_combination: _Optional[int] = ..., items: _Optional[_Union[ArrayOfResultCombinationItems, _Mapping]] = ..., generate_subcombinations: bool = ..., load_duration: _Optional[str] = ..., is_generated: bool = ..., consider_construction_stage: _Optional[int] = ..., consider_construction_stage_active: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfResultCombinationItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
