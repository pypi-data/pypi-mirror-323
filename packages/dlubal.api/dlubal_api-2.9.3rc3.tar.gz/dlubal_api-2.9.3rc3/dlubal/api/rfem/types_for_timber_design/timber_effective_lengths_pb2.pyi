from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimberEffectiveLengthsBucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIMBER_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[TimberEffectiveLengthsBucklingFactorValueType]
    TIMBER_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[TimberEffectiveLengthsBucklingFactorValueType]

class TimberEffectiveLengthsDeterminationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_ANALYTICAL: _ClassVar[TimberEffectiveLengthsDeterminationType]
    TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_EIGENVALUE_SOLVER: _ClassVar[TimberEffectiveLengthsDeterminationType]
    TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_USER_DEFINED: _ClassVar[TimberEffectiveLengthsDeterminationType]
TIMBER_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: TimberEffectiveLengthsBucklingFactorValueType
TIMBER_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: TimberEffectiveLengthsBucklingFactorValueType
TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_ANALYTICAL: TimberEffectiveLengthsDeterminationType
TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_EIGENVALUE_SOLVER: TimberEffectiveLengthsDeterminationType
TIMBER_EFFECTIVE_LENGTHS_DETERMINATION_TYPE_USER_DEFINED: TimberEffectiveLengthsDeterminationType

class TimberEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "flexural_buckling_about_y", "flexural_buckling_about_z", "lateral_torsional_buckling", "buckling_factor_value_type", "is_generated", "generating_object_info", "intermediate_nodes", "different_properties", "factors_definition_absolute", "nodal_supports", "factors", "lengths", "fire_design_nodal_supports", "fire_design_factors", "fire_design_lengths", "fire_design_intermediate_nodes", "fire_design_different_properties", "fire_design_factors_definition_absolute", "fire_design_different_buckling_factors", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "determination_type", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_FACTORS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    FIRE_DESIGN_DIFFERENT_BUCKLING_FACTORS_FIELD_NUMBER: _ClassVar[int]
    IMPORT_FROM_STABILITY_ANALYSIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MEMBER_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LOADING_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MODE_NUMBER_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MEMBER_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LOADING_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_MODE_NUMBER_Z_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_FACTORS_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_USER_DEFINED_Y_FIELD_NUMBER: _ClassVar[int]
    STABILITY_IMPORT_DATA_USER_DEFINED_Z_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    flexural_buckling_about_y: bool
    flexural_buckling_about_z: bool
    lateral_torsional_buckling: bool
    buckling_factor_value_type: TimberEffectiveLengthsBucklingFactorValueType
    is_generated: bool
    generating_object_info: str
    intermediate_nodes: bool
    different_properties: bool
    factors_definition_absolute: bool
    nodal_supports: ArrayOfTimberEffectiveLengthsNodalSupports
    factors: ArrayOfTimberEffectiveLengthsFactors
    lengths: ArrayOfTimberEffectiveLengthsLengths
    fire_design_nodal_supports: ArrayOfTimberEffectiveLengthsFireDesignNodalSupports
    fire_design_factors: ArrayOfTimberEffectiveLengthsFireDesignFactors
    fire_design_lengths: ArrayOfTimberEffectiveLengthsFireDesignLengths
    fire_design_intermediate_nodes: bool
    fire_design_different_properties: bool
    fire_design_factors_definition_absolute: bool
    fire_design_different_buckling_factors: bool
    import_from_stability_analysis_enabled: bool
    stability_import_data_factors_definition_absolute: bool
    stability_import_data_member_y: int
    stability_import_data_loading_y: int
    stability_import_data_mode_number_y: int
    stability_import_data_member_z: int
    stability_import_data_loading_z: int
    stability_import_data_mode_number_z: int
    stability_import_data_factors: ArrayOfTimberEffectiveLengthsStabilityImportDataFactors
    stability_import_data_lengths: ArrayOfTimberEffectiveLengthsStabilityImportDataLengths
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    determination_type: TimberEffectiveLengthsDeterminationType
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[TimberEffectiveLengthsBucklingFactorValueType, str]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., factors_definition_absolute: bool = ..., nodal_supports: _Optional[_Union[ArrayOfTimberEffectiveLengthsNodalSupports, _Mapping]] = ..., factors: _Optional[_Union[ArrayOfTimberEffectiveLengthsFactors, _Mapping]] = ..., lengths: _Optional[_Union[ArrayOfTimberEffectiveLengthsLengths, _Mapping]] = ..., fire_design_nodal_supports: _Optional[_Union[ArrayOfTimberEffectiveLengthsFireDesignNodalSupports, _Mapping]] = ..., fire_design_factors: _Optional[_Union[ArrayOfTimberEffectiveLengthsFireDesignFactors, _Mapping]] = ..., fire_design_lengths: _Optional[_Union[ArrayOfTimberEffectiveLengthsFireDesignLengths, _Mapping]] = ..., fire_design_intermediate_nodes: bool = ..., fire_design_different_properties: bool = ..., fire_design_factors_definition_absolute: bool = ..., fire_design_different_buckling_factors: bool = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[int] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[int] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[ArrayOfTimberEffectiveLengthsStabilityImportDataFactors, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[ArrayOfTimberEffectiveLengthsStabilityImportDataLengths, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., determination_type: _Optional[_Union[TimberEffectiveLengthsDeterminationType, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfTimberEffectiveLengthsNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsFireDesignNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsFireDesignFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsFireDesignLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsStabilityImportDataFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfTimberEffectiveLengthsStabilityImportDataLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
