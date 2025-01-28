from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadCombinationAnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAD_COMBINATION_ANALYSIS_TYPE_UNKNOWN: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_HARMONIC_RESPONSE_ANALYSIS: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_PUSHOVER: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_STATIC: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_STATIC_CREEP_AND_SHRINKAGE: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_STATIC_TIME_DEPENDENCE: _ClassVar[LoadCombinationAnalysisType]
    LOAD_COMBINATION_ANALYSIS_TYPE_TIME_HISTORY_TIME_DIAGRAM: _ClassVar[LoadCombinationAnalysisType]

class LoadCombinationInitialStateDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: _ClassVar[LoadCombinationInitialStateDefinitionType]
    LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: _ClassVar[LoadCombinationInitialStateDefinitionType]
    LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS: _ClassVar[LoadCombinationInitialStateDefinitionType]
    LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: _ClassVar[LoadCombinationInitialStateDefinitionType]

class LoadCombinationPushoverDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAD_COMBINATION_PUSHOVER_DIRECTION_X: _ClassVar[LoadCombinationPushoverDirection]
    LOAD_COMBINATION_PUSHOVER_DIRECTION_MINUS_X: _ClassVar[LoadCombinationPushoverDirection]
    LOAD_COMBINATION_PUSHOVER_DIRECTION_MINUS_Y: _ClassVar[LoadCombinationPushoverDirection]
    LOAD_COMBINATION_PUSHOVER_DIRECTION_Y: _ClassVar[LoadCombinationPushoverDirection]

class LoadCombinationPushoverNormalizedDisplacements(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_UNIFORM: _ClassVar[LoadCombinationPushoverNormalizedDisplacements]
    LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_MODAL_AUTOMATIC_MODAL_SHAPE: _ClassVar[LoadCombinationPushoverNormalizedDisplacements]
    LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_MODAL_USER_SELECTED_MODAL_SHAPE: _ClassVar[LoadCombinationPushoverNormalizedDisplacements]
LOAD_COMBINATION_ANALYSIS_TYPE_UNKNOWN: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_HARMONIC_RESPONSE_ANALYSIS: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_PUSHOVER: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_STATIC: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_STATIC_CREEP_AND_SHRINKAGE: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_STATIC_TIME_DEPENDENCE: LoadCombinationAnalysisType
LOAD_COMBINATION_ANALYSIS_TYPE_TIME_HISTORY_TIME_DIAGRAM: LoadCombinationAnalysisType
LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: LoadCombinationInitialStateDefinitionType
LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: LoadCombinationInitialStateDefinitionType
LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS: LoadCombinationInitialStateDefinitionType
LOAD_COMBINATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: LoadCombinationInitialStateDefinitionType
LOAD_COMBINATION_PUSHOVER_DIRECTION_X: LoadCombinationPushoverDirection
LOAD_COMBINATION_PUSHOVER_DIRECTION_MINUS_X: LoadCombinationPushoverDirection
LOAD_COMBINATION_PUSHOVER_DIRECTION_MINUS_Y: LoadCombinationPushoverDirection
LOAD_COMBINATION_PUSHOVER_DIRECTION_Y: LoadCombinationPushoverDirection
LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_UNIFORM: LoadCombinationPushoverNormalizedDisplacements
LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_MODAL_AUTOMATIC_MODAL_SHAPE: LoadCombinationPushoverNormalizedDisplacements
LOAD_COMBINATION_PUSHOVER_NORMALIZED_DISPLACEMENTS_MODAL_USER_SELECTED_MODAL_SHAPE: LoadCombinationPushoverNormalizedDisplacements

class LoadCombination(_message.Message):
    __slots__ = ("no", "analysis_type", "design_situation", "user_defined_name_enabled", "name", "static_analysis_settings", "import_modal_analysis_load_case", "calculate_critical_load", "stability_analysis_settings", "consider_imperfection", "imperfection_case", "consider_initial_state", "initial_state_case", "consider_construction_stage", "construction_stage", "creep_loading_case", "sustained_load_enabled", "sustained_load", "sway_load_enabled", "sway_load", "structure_modification_enabled", "structure_modification", "to_solve", "comment", "load_duration", "items", "loading_start", "time_being_investigated", "is_generated", "generating_object_info", "initial_state_definition_type", "individual_factors_of_selected_objects_table", "geotechnical_analysis_reset_small_strain_history", "pushover_vertical_loads_case", "pushover_modal_analysis_from_load_case", "pushover_direction", "pushover_normalized_displacements", "pushover_mode_shape_number", "pushover_response_spectrum", "pushover_response_spectrum_scale_factor", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SITUATION_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATIC_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    IMPORT_MODAL_ANALYSIS_LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    CALCULATE_CRITICAL_LOAD_FIELD_NUMBER: _ClassVar[int]
    STABILITY_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_IMPERFECTION_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_CASE_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    CREEP_LOADING_CASE_FIELD_NUMBER: _ClassVar[int]
    SUSTAINED_LOAD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SUSTAINED_LOAD_FIELD_NUMBER: _ClassVar[int]
    SWAY_LOAD_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SWAY_LOAD_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    TO_SOLVE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOAD_DURATION_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    LOADING_START_FIELD_NUMBER: _ClassVar[int]
    TIME_BEING_INVESTIGATED_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_FACTORS_OF_SELECTED_OBJECTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    GEOTECHNICAL_ANALYSIS_RESET_SMALL_STRAIN_HISTORY_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_VERTICAL_LOADS_CASE_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_MODAL_ANALYSIS_FROM_LOAD_CASE_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_NORMALIZED_DISPLACEMENTS_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_MODE_SHAPE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_RESPONSE_SPECTRUM_FIELD_NUMBER: _ClassVar[int]
    PUSHOVER_RESPONSE_SPECTRUM_SCALE_FACTOR_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    analysis_type: LoadCombinationAnalysisType
    design_situation: int
    user_defined_name_enabled: bool
    name: str
    static_analysis_settings: int
    import_modal_analysis_load_case: int
    calculate_critical_load: bool
    stability_analysis_settings: int
    consider_imperfection: bool
    imperfection_case: int
    consider_initial_state: bool
    initial_state_case: int
    consider_construction_stage: bool
    construction_stage: int
    creep_loading_case: int
    sustained_load_enabled: bool
    sustained_load: int
    sway_load_enabled: bool
    sway_load: int
    structure_modification_enabled: bool
    structure_modification: int
    to_solve: bool
    comment: str
    load_duration: str
    items: ArrayOfLoadCombinationItems
    loading_start: float
    time_being_investigated: float
    is_generated: bool
    generating_object_info: str
    initial_state_definition_type: LoadCombinationInitialStateDefinitionType
    individual_factors_of_selected_objects_table: ArrayOfLoadCombinationIndividualFactorsOfSelectedObjectsTable
    geotechnical_analysis_reset_small_strain_history: bool
    pushover_vertical_loads_case: int
    pushover_modal_analysis_from_load_case: int
    pushover_direction: LoadCombinationPushoverDirection
    pushover_normalized_displacements: LoadCombinationPushoverNormalizedDisplacements
    pushover_mode_shape_number: int
    pushover_response_spectrum: int
    pushover_response_spectrum_scale_factor: float
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., analysis_type: _Optional[_Union[LoadCombinationAnalysisType, str]] = ..., design_situation: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., static_analysis_settings: _Optional[int] = ..., import_modal_analysis_load_case: _Optional[int] = ..., calculate_critical_load: bool = ..., stability_analysis_settings: _Optional[int] = ..., consider_imperfection: bool = ..., imperfection_case: _Optional[int] = ..., consider_initial_state: bool = ..., initial_state_case: _Optional[int] = ..., consider_construction_stage: bool = ..., construction_stage: _Optional[int] = ..., creep_loading_case: _Optional[int] = ..., sustained_load_enabled: bool = ..., sustained_load: _Optional[int] = ..., sway_load_enabled: bool = ..., sway_load: _Optional[int] = ..., structure_modification_enabled: bool = ..., structure_modification: _Optional[int] = ..., to_solve: bool = ..., comment: _Optional[str] = ..., load_duration: _Optional[str] = ..., items: _Optional[_Union[ArrayOfLoadCombinationItems, _Mapping]] = ..., loading_start: _Optional[float] = ..., time_being_investigated: _Optional[float] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., initial_state_definition_type: _Optional[_Union[LoadCombinationInitialStateDefinitionType, str]] = ..., individual_factors_of_selected_objects_table: _Optional[_Union[ArrayOfLoadCombinationIndividualFactorsOfSelectedObjectsTable, _Mapping]] = ..., geotechnical_analysis_reset_small_strain_history: bool = ..., pushover_vertical_loads_case: _Optional[int] = ..., pushover_modal_analysis_from_load_case: _Optional[int] = ..., pushover_direction: _Optional[_Union[LoadCombinationPushoverDirection, str]] = ..., pushover_normalized_displacements: _Optional[_Union[LoadCombinationPushoverNormalizedDisplacements, str]] = ..., pushover_mode_shape_number: _Optional[int] = ..., pushover_response_spectrum: _Optional[int] = ..., pushover_response_spectrum_scale_factor: _Optional[float] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfLoadCombinationItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfLoadCombinationIndividualFactorsOfSelectedObjectsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
