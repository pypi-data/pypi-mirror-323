from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AluminumEffectiveLengthsBucklingFactorValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALUMINUM_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: _ClassVar[AluminumEffectiveLengthsBucklingFactorValueType]
    ALUMINUM_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: _ClassVar[AluminumEffectiveLengthsBucklingFactorValueType]

class AluminumEffectiveLengthsDeterminationMcrEurope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_MCR_EUROPE_EIGENVALUE: _ClassVar[AluminumEffectiveLengthsDeterminationMcrEurope]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_MCR_EUROPE_USER_DEFINED: _ClassVar[AluminumEffectiveLengthsDeterminationMcrEurope]

class AluminumEffectiveLengthsDeterminationMeAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_EIGENVALUE_METHOD: _ClassVar[AluminumEffectiveLengthsDeterminationMeAdm]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_ACC_TO_CHAPTER_F: _ClassVar[AluminumEffectiveLengthsDeterminationMeAdm]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_USER_DEFINED: _ClassVar[AluminumEffectiveLengthsDeterminationMeAdm]

class AluminumEffectiveLengthsDeterminationCbAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_BASIC_VALUE: _ClassVar[AluminumEffectiveLengthsDeterminationCbAdm]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_AUTOMATICALLY_ACC_TO_F_4_1: _ClassVar[AluminumEffectiveLengthsDeterminationCbAdm]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_USER_DEFINED: _ClassVar[AluminumEffectiveLengthsDeterminationCbAdm]

class AluminumEffectiveLengthsDeterminationCbMemberTypeAdm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_MEMBER_TYPE_ADM_BEAM: _ClassVar[AluminumEffectiveLengthsDeterminationCbMemberTypeAdm]
    ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_MEMBER_TYPE_ADM_CANTILEVER: _ClassVar[AluminumEffectiveLengthsDeterminationCbMemberTypeAdm]
ALUMINUM_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_THEORETICAL: AluminumEffectiveLengthsBucklingFactorValueType
ALUMINUM_EFFECTIVE_LENGTHS_BUCKLING_FACTOR_VALUE_TYPE_RECOMMENDED: AluminumEffectiveLengthsBucklingFactorValueType
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_MCR_EUROPE_EIGENVALUE: AluminumEffectiveLengthsDeterminationMcrEurope
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_MCR_EUROPE_USER_DEFINED: AluminumEffectiveLengthsDeterminationMcrEurope
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_EIGENVALUE_METHOD: AluminumEffectiveLengthsDeterminationMeAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_ACC_TO_CHAPTER_F: AluminumEffectiveLengthsDeterminationMeAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_ME_ADM_USER_DEFINED: AluminumEffectiveLengthsDeterminationMeAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_BASIC_VALUE: AluminumEffectiveLengthsDeterminationCbAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_AUTOMATICALLY_ACC_TO_F_4_1: AluminumEffectiveLengthsDeterminationCbAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_ADM_USER_DEFINED: AluminumEffectiveLengthsDeterminationCbAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_MEMBER_TYPE_ADM_BEAM: AluminumEffectiveLengthsDeterminationCbMemberTypeAdm
ALUMINUM_EFFECTIVE_LENGTHS_DETERMINATION_CB_MEMBER_TYPE_ADM_CANTILEVER: AluminumEffectiveLengthsDeterminationCbMemberTypeAdm

class AluminumEffectiveLengths(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "comment", "members", "member_sets", "flexural_buckling_about_y", "flexural_buckling_about_z", "torsional_buckling", "lateral_torsional_buckling", "buckling_factor_value_type", "principal_section_axes", "geometric_section_axes", "is_generated", "generating_object_info", "factors_definition_absolute", "intermediate_nodes", "different_properties", "determination_mcr_europe", "determination_me_adm", "determination_cb_adm", "cb_factor_adm", "determination_cb_member_type_adm", "nodal_supports", "factors", "lengths", "import_from_stability_analysis_enabled", "stability_import_data_factors_definition_absolute", "stability_import_data_member_y", "stability_import_data_loading_y", "stability_import_data_mode_number_y", "stability_import_data_member_z", "stability_import_data_loading_z", "stability_import_data_mode_number_z", "stability_import_data_factors", "stability_import_data_lengths", "stability_import_data_user_defined_y", "stability_import_data_user_defined_z", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Y_FIELD_NUMBER: _ClassVar[int]
    FLEXURAL_BUCKLING_ABOUT_Z_FIELD_NUMBER: _ClassVar[int]
    TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    LATERAL_TORSIONAL_BUCKLING_FIELD_NUMBER: _ClassVar[int]
    BUCKLING_FACTOR_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_SECTION_AXES_FIELD_NUMBER: _ClassVar[int]
    GEOMETRIC_SECTION_AXES_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    FACTORS_DEFINITION_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_NODES_FIELD_NUMBER: _ClassVar[int]
    DIFFERENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_MCR_EUROPE_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_ME_ADM_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_ADM_FIELD_NUMBER: _ClassVar[int]
    CB_FACTOR_ADM_FIELD_NUMBER: _ClassVar[int]
    DETERMINATION_CB_MEMBER_TYPE_ADM_FIELD_NUMBER: _ClassVar[int]
    NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    LENGTHS_FIELD_NUMBER: _ClassVar[int]
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
    torsional_buckling: bool
    lateral_torsional_buckling: bool
    buckling_factor_value_type: AluminumEffectiveLengthsBucklingFactorValueType
    principal_section_axes: bool
    geometric_section_axes: bool
    is_generated: bool
    generating_object_info: str
    factors_definition_absolute: bool
    intermediate_nodes: bool
    different_properties: bool
    determination_mcr_europe: AluminumEffectiveLengthsDeterminationMcrEurope
    determination_me_adm: AluminumEffectiveLengthsDeterminationMeAdm
    determination_cb_adm: AluminumEffectiveLengthsDeterminationCbAdm
    cb_factor_adm: float
    determination_cb_member_type_adm: AluminumEffectiveLengthsDeterminationCbMemberTypeAdm
    nodal_supports: ArrayOfAluminumEffectiveLengthsNodalSupports
    factors: ArrayOfAluminumEffectiveLengthsFactors
    lengths: ArrayOfAluminumEffectiveLengthsLengths
    import_from_stability_analysis_enabled: bool
    stability_import_data_factors_definition_absolute: bool
    stability_import_data_member_y: int
    stability_import_data_loading_y: int
    stability_import_data_mode_number_y: int
    stability_import_data_member_z: int
    stability_import_data_loading_z: int
    stability_import_data_mode_number_z: int
    stability_import_data_factors: ArrayOfAluminumEffectiveLengthsStabilityImportDataFactors
    stability_import_data_lengths: ArrayOfAluminumEffectiveLengthsStabilityImportDataLengths
    stability_import_data_user_defined_y: bool
    stability_import_data_user_defined_z: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., comment: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., flexural_buckling_about_y: bool = ..., flexural_buckling_about_z: bool = ..., torsional_buckling: bool = ..., lateral_torsional_buckling: bool = ..., buckling_factor_value_type: _Optional[_Union[AluminumEffectiveLengthsBucklingFactorValueType, str]] = ..., principal_section_axes: bool = ..., geometric_section_axes: bool = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., factors_definition_absolute: bool = ..., intermediate_nodes: bool = ..., different_properties: bool = ..., determination_mcr_europe: _Optional[_Union[AluminumEffectiveLengthsDeterminationMcrEurope, str]] = ..., determination_me_adm: _Optional[_Union[AluminumEffectiveLengthsDeterminationMeAdm, str]] = ..., determination_cb_adm: _Optional[_Union[AluminumEffectiveLengthsDeterminationCbAdm, str]] = ..., cb_factor_adm: _Optional[float] = ..., determination_cb_member_type_adm: _Optional[_Union[AluminumEffectiveLengthsDeterminationCbMemberTypeAdm, str]] = ..., nodal_supports: _Optional[_Union[ArrayOfAluminumEffectiveLengthsNodalSupports, _Mapping]] = ..., factors: _Optional[_Union[ArrayOfAluminumEffectiveLengthsFactors, _Mapping]] = ..., lengths: _Optional[_Union[ArrayOfAluminumEffectiveLengthsLengths, _Mapping]] = ..., import_from_stability_analysis_enabled: bool = ..., stability_import_data_factors_definition_absolute: bool = ..., stability_import_data_member_y: _Optional[int] = ..., stability_import_data_loading_y: _Optional[int] = ..., stability_import_data_mode_number_y: _Optional[int] = ..., stability_import_data_member_z: _Optional[int] = ..., stability_import_data_loading_z: _Optional[int] = ..., stability_import_data_mode_number_z: _Optional[int] = ..., stability_import_data_factors: _Optional[_Union[ArrayOfAluminumEffectiveLengthsStabilityImportDataFactors, _Mapping]] = ..., stability_import_data_lengths: _Optional[_Union[ArrayOfAluminumEffectiveLengthsStabilityImportDataLengths, _Mapping]] = ..., stability_import_data_user_defined_y: bool = ..., stability_import_data_user_defined_z: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfAluminumEffectiveLengthsNodalSupports(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfAluminumEffectiveLengthsFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfAluminumEffectiveLengthsLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfAluminumEffectiveLengthsStabilityImportDataFactors(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfAluminumEffectiveLengthsStabilityImportDataLengths(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
