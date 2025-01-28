from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WindSimulationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WIND_SIMULATION_TYPE_UNKNOWN: _ClassVar[WindSimulationType]
    WIND_SIMULATION_TYPE_STANDARD: _ClassVar[WindSimulationType]

class WindSimulationWindDirectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WIND_SIMULATION_WIND_DIRECTION_TYPE_UNIFORM: _ClassVar[WindSimulationWindDirectionType]
    WIND_SIMULATION_WIND_DIRECTION_TYPE_USER_DEFINED: _ClassVar[WindSimulationWindDirectionType]

class WindSimulationInitialStateDefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: _ClassVar[WindSimulationInitialStateDefinitionType]
    WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: _ClassVar[WindSimulationInitialStateDefinitionType]
    WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS: _ClassVar[WindSimulationInitialStateDefinitionType]
    WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: _ClassVar[WindSimulationInitialStateDefinitionType]
WIND_SIMULATION_TYPE_UNKNOWN: WindSimulationType
WIND_SIMULATION_TYPE_STANDARD: WindSimulationType
WIND_SIMULATION_WIND_DIRECTION_TYPE_UNIFORM: WindSimulationWindDirectionType
WIND_SIMULATION_WIND_DIRECTION_TYPE_USER_DEFINED: WindSimulationWindDirectionType
WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_FINAL_STATE: WindSimulationInitialStateDefinitionType
WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STIFFNESS: WindSimulationInitialStateDefinitionType
WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS: WindSimulationInitialStateDefinitionType
WIND_SIMULATION_INITIAL_STATE_DEFINITION_TYPE_STRAINS_WITH_USER_DEFINED_FACTORS: WindSimulationInitialStateDefinitionType

class WindSimulation(_message.Message):
    __slots__ = ("no", "type", "user_defined_name_enabled", "name", "active", "wind_profile", "wind_simulation_analysis_settings", "wind_direction_type", "uniform_wind_direction_step", "uniform_wind_direction_range_start", "uniform_wind_direction_range_end", "user_defined_list_of_wind_directions", "generate_into_load_cases", "consider_initial_state", "initial_state_case", "initial_state_definition_type", "individual_factors_of_selected_objects_table", "comment", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    WIND_PROFILE_FIELD_NUMBER: _ClassVar[int]
    WIND_SIMULATION_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    WIND_DIRECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_STEP_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_RANGE_START_FIELD_NUMBER: _ClassVar[int]
    UNIFORM_WIND_DIRECTION_RANGE_END_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_LIST_OF_WIND_DIRECTIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATE_INTO_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_CASE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_FACTORS_OF_SELECTED_OBJECTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: WindSimulationType
    user_defined_name_enabled: bool
    name: str
    active: bool
    wind_profile: int
    wind_simulation_analysis_settings: int
    wind_direction_type: WindSimulationWindDirectionType
    uniform_wind_direction_step: float
    uniform_wind_direction_range_start: float
    uniform_wind_direction_range_end: float
    user_defined_list_of_wind_directions: _containers.RepeatedScalarFieldContainer[int]
    generate_into_load_cases: ArrayOfWindSimulationGenerateIntoLoadCases
    consider_initial_state: bool
    initial_state_case: int
    initial_state_definition_type: WindSimulationInitialStateDefinitionType
    individual_factors_of_selected_objects_table: ArrayOfWindSimulationIndividualFactorsOfSelectedObjectsTable
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[WindSimulationType, str]] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., active: bool = ..., wind_profile: _Optional[int] = ..., wind_simulation_analysis_settings: _Optional[int] = ..., wind_direction_type: _Optional[_Union[WindSimulationWindDirectionType, str]] = ..., uniform_wind_direction_step: _Optional[float] = ..., uniform_wind_direction_range_start: _Optional[float] = ..., uniform_wind_direction_range_end: _Optional[float] = ..., user_defined_list_of_wind_directions: _Optional[_Iterable[int]] = ..., generate_into_load_cases: _Optional[_Union[ArrayOfWindSimulationGenerateIntoLoadCases, _Mapping]] = ..., consider_initial_state: bool = ..., initial_state_case: _Optional[int] = ..., initial_state_definition_type: _Optional[_Union[WindSimulationInitialStateDefinitionType, str]] = ..., individual_factors_of_selected_objects_table: _Optional[_Union[ArrayOfWindSimulationIndividualFactorsOfSelectedObjectsTable, _Mapping]] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfWindSimulationGenerateIntoLoadCases(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfWindSimulationIndividualFactorsOfSelectedObjectsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
