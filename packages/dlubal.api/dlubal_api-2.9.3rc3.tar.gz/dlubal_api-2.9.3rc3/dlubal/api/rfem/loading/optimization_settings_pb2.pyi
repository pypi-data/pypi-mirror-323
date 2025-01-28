from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OptimizationSettingsTargetValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_TOTAL_WEIGHT: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MAX_GLOBAL_PARAMETER: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_CO2_EMISSIONS: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_COST: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_GLOBAL_PARAMETER: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_MEMBER_DEFORMATION: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_NODAL_DEFORMATION: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_SURFACE_DEFORMATION: _ClassVar[OptimizationSettingsTargetValueType]
    OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_VECTORIAL_DISPLACEMENT: _ClassVar[OptimizationSettingsTargetValueType]

class OptimizationSettingsOptimizerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_ALL_MUTATIONS: _ClassVar[OptimizationSettingsOptimizerType]
    OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_ANT_COLONY: _ClassVar[OptimizationSettingsOptimizerType]
    OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_PARTICLE_SWARM: _ClassVar[OptimizationSettingsOptimizerType]
    OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_RANDOM_MUTATIONS: _ClassVar[OptimizationSettingsOptimizerType]
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_TOTAL_WEIGHT: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MAX_GLOBAL_PARAMETER: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_CO2_EMISSIONS: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_COST: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_GLOBAL_PARAMETER: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_MEMBER_DEFORMATION: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_NODAL_DEFORMATION: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_SURFACE_DEFORMATION: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_TARGET_VALUE_TYPE_MIN_VECTORIAL_DISPLACEMENT: OptimizationSettingsTargetValueType
OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_ALL_MUTATIONS: OptimizationSettingsOptimizerType
OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_ANT_COLONY: OptimizationSettingsOptimizerType
OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_PARTICLE_SWARM: OptimizationSettingsOptimizerType
OPTIMIZATION_SETTINGS_OPTIMIZER_TYPE_RANDOM_MUTATIONS: OptimizationSettingsOptimizerType

class OptimizationSettings(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "active", "target_value_type", "target_global_parameter", "optimizer_type", "percent_of_mutations", "optimization_values_table", "total_number_of_mutations", "comment", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TARGET_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_GLOBAL_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZER_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERCENT_OF_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_VALUES_TABLE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NUMBER_OF_MUTATIONS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    active: bool
    target_value_type: OptimizationSettingsTargetValueType
    target_global_parameter: int
    optimizer_type: OptimizationSettingsOptimizerType
    percent_of_mutations: float
    optimization_values_table: ArrayOfOptimizationSettingsOptimizationValuesTable
    total_number_of_mutations: int
    comment: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., active: bool = ..., target_value_type: _Optional[_Union[OptimizationSettingsTargetValueType, str]] = ..., target_global_parameter: _Optional[int] = ..., optimizer_type: _Optional[_Union[OptimizationSettingsOptimizerType, str]] = ..., percent_of_mutations: _Optional[float] = ..., optimization_values_table: _Optional[_Union[ArrayOfOptimizationSettingsOptimizationValuesTable, _Mapping]] = ..., total_number_of_mutations: _Optional[int] = ..., comment: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfOptimizationSettingsOptimizationValuesTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
