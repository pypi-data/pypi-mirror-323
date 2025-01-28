from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteEffectiveLengthsBucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[ConcreteEffectiveLengthsBucklingFactorValueType]
    CONCRETE_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[ConcreteEffectiveLengthsBucklingFactorValueType]

class ConcreteEffectiveLengthsStructureTypeAboutAxisY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_UNBRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisY]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_BRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisY]

class ConcreteEffectiveLengthsStructureTypeAboutAxisZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_UNBRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisZ]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_BRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisZ]

class ConcreteEffectiveLengthsStructuralSchemeAboutAxisY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Y_DETERMINED: _ClassVar[ConcreteEffectiveLengthsStructuralSchemeAboutAxisY]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Y_NON_DETERMINED: _ClassVar[ConcreteEffectiveLengthsStructuralSchemeAboutAxisY]

class ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Z_DETERMINED: _ClassVar[ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Z_NON_DETERMINED: _ClassVar[ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ]

class ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_UNBRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_BRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_COMBINED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63]

class ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_UNBRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_BRACED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63]
    CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_COMBINED: _ClassVar[ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63]
CONCRETE_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: ConcreteEffectiveLengthsBucklingFactorValueType
CONCRETE_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: ConcreteEffectiveLengthsBucklingFactorValueType
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_UNBRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisY
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_BRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisY
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_UNBRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisZ
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_BRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisZ
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Y_DETERMINED: ConcreteEffectiveLengthsStructuralSchemeAboutAxisY
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Y_NON_DETERMINED: ConcreteEffectiveLengthsStructuralSchemeAboutAxisY
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Z_DETERMINED: ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURAL_SCHEME_ABOUT_AXIS_Z_NON_DETERMINED: ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_UNBRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_BRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_COMBINED: ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_UNBRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_BRACED: ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63
CONCRETE_EFFECTIVE_LENGTHS_STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_COMBINED: ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63

class ConcreteEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "lateral_torsional_buckling", "buckling_factor_value_type", "is_generated", "generating_object_info", "intermediate_nodes", "different_properties", "factors_definition_absolute", "fire_design_nodal_supports", "fire_design_factors", "fire_design_lengths", "fire_design_intermediate_nodes", "fire_design_different_properties", "fire_design_factors_definition_absolute", "fire_design_different_buckling_factors", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "structure_type_about_axis_y", "structure_type_about_axis_z", "structural_scheme_about_axis_y", "structural_scheme_about_axis_z", "flexural_buckling_about_y", "flexural_buckling_about_z", "nodal_supports", "factors", "lengths", "structure_type_about_axis_y_sp63", "structure_type_about_axis_z_sp63", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
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
    STRUCTURE_TYPE_ABOUT_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Y_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_SCHEME_ABOUT_AXIS_Z_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Y_SP63_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_TYPE_ABOUT_AXIS_Z_SP63_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    comment: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    lateral_torsional_buckling: bool
    buckling_factor_value_type: ConcreteEffectiveLengthsBucklingFactorValueType
    is_generated: bool
    generating_object_info: str
    intermediate_nodes: bool
    different_properties: bool
    factors_definition_absolute: bool
    fire_design_nodal_supports: ArrayOfConcreteEffectiveLengthsFireDesignNodalSupports
    fire_design_factors: ArrayOfConcreteEffectiveLengthsFireDesignFactors
    fire_design_lengths: ArrayOfConcreteEffectiveLengthsFireDesignLengths
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
    stability_import_data_factors: ArrayOfConcreteEffectiveLengthsStabilityImportDataFactors
    stability_import_data_lengths: ArrayOfConcreteEffectiveLengthsStabilityImportDataLengths
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    structure_type_about_axis_y: ConcreteEffectiveLengthsStructureTypeAboutAxisY
    structure_type_about_axis_z: ConcreteEffectiveLengthsStructureTypeAboutAxisZ
    structural_scheme_about_axis_y: ConcreteEffectiveLengthsStructuralSchemeAboutAxisY
    structural_scheme_about_axis_z: ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ
    flexural_buckling_about_y: bool
    flexural_buckling_about_z: bool
    nodal_supports: ArrayOfConcreteEffectiveLengthsNodalSupports
    factors: ArrayOfConcreteEffectiveLengthsFactors
    lengths: ArrayOfConcreteEffectiveLengthsLengths
    structure_type_about_axis_y_sp63: ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63
    structure_type_about_axis_z_sp63: ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[ConcreteEffectiveLengthsBucklingFactorValueType, str]] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., factors_definition_absolute: bool = ..., fire_design_nodal_supports: _Optional[_Union[ArrayOfConcreteEffectiveLengthsFireDesignNodalSupports, _Mapping]] = ..., fire_design_factors: _Optional[_Union[ArrayOfConcreteEffectiveLengthsFireDesignFactors, _Mapping]] = ..., fire_design_lengths: _Optional[_Union[ArrayOfConcreteEffectiveLengthsFireDesignLengths, _Mapping]] = ..., fire_design_intermediate_nodes: bool = ..., fire_design_different_properties: bool = ..., fire_design_factors_definition_absolute: bool = ..., fire_design_different_buckling_factors: bool = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[int] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[int] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[ArrayOfConcreteEffectiveLengthsStabilityImportDataFactors, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[ArrayOfConcreteEffectiveLengthsStabilityImportDataLengths, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., structure_type_about_axis_y: _Optional[_Union[ConcreteEffectiveLengthsStructureTypeAboutAxisY, str]] = ..., structure_type_about_axis_z: _Optional[_Union[ConcreteEffectiveLengthsStructureTypeAboutAxisZ, str]] = ..., structural_scheme_about_axis_y: _Optional[_Union[ConcreteEffectiveLengthsStructuralSchemeAboutAxisY, str]] = ..., structural_scheme_about_axis_z: _Optional[_Union[ConcreteEffectiveLengthsStructuralSchemeAboutAxisZ, str]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., nodal_supports: _Optional[_Union[ArrayOfConcreteEffectiveLengthsNodalSupports, _Mapping]] = ..., factors: _Optional[_Union[ArrayOfConcreteEffectiveLengthsFactors, _Mapping]] = ..., lengths: _Optional[_Union[ArrayOfConcreteEffectiveLengthsLengths, _Mapping]] = ..., structure_type_about_axis_y_sp63: _Optional[_Union[ConcreteEffectiveLengthsStructureTypeAboutAxisYSp63, str]] = ..., structure_type_about_axis_z_sp63: _Optional[_Union[ConcreteEffectiveLengthsStructureTypeAboutAxisZSp63, str]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfConcreteEffectiveLengthsFireDesignNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsFireDesignFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsFireDesignLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsStabilityImportDataFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsStabilityImportDataLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConcreteEffectiveLengthsLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
