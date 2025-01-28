from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CombinationWizardGenerateCombinations(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMBINATION_WIZARD_GENERATE_COMBINATIONS_LOAD_COMBINATIONS: _ClassVar[CombinationWizardGenerateCombinations]
    COMBINATION_WIZARD_GENERATE_COMBINATIONS_RESULT_COMBINATIONS: _ClassVar[CombinationWizardGenerateCombinations]
COMBINATION_WIZARD_GENERATE_COMBINATIONS_LOAD_COMBINATIONS: CombinationWizardGenerateCombinations
COMBINATION_WIZARD_GENERATE_COMBINATIONS_RESULT_COMBINATIONS: CombinationWizardGenerateCombinations

class CombinationWizard(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "static_analysis_settings", "generate_combinations", "has_stability_analysis", "stability_analysis_settings", "consider_imperfection_case", "generate_same_CO_without_IC", "generate_co_without_initial_state", "user_defined_action_combinations", "favorable_permanent_actions", "reduce_number_of_generated_combinations", "auxiliary_combinations", "generate_subcombinations_of_type_superposition", "comment", "consider_initial_state", "initial_state_items", "structure_modification_enabled", "structure_modification", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATIC_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    GENERATE_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    HAS_STABILITY_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    STABILITY_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    GENERATE_SAME_CO_WITHOUT_IC_FIELD_NUMBER: _ClassVar[int]
    GENERATE_CO_WITHOUT_INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_ACTION_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    FAVORABLE_PERMANENT_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    REDUCE_NUMBER_OF_GENERATED_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    AUXILIARY_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    GENERATE_SUBCOMBINATIONS_OF_TYPE_SUPERPOSITION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_INITIAL_STATE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STATE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    static_analysis_settings: int
    generate_combinations: CombinationWizardGenerateCombinations
    has_stability_analysis: bool
    stability_analysis_settings: int
    consider_imperfection_case: bool
    generate_same_CO_without_IC: bool
    generate_co_without_initial_state: bool
    user_defined_action_combinations: bool
    favorable_permanent_actions: bool
    reduce_number_of_generated_combinations: bool
    auxiliary_combinations: bool
    generate_subcombinations_of_type_superposition: bool
    comment: str
    consider_initial_state: bool
    initial_state_items: ArrayOfCombinationWizardInitialStateItems
    structure_modification_enabled: bool
    structure_modification: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., static_analysis_settings: _Optional[int] = ..., generate_combinations: _Optional[_Union[CombinationWizardGenerateCombinations, str]] = ..., has_stability_analysis: bool = ..., stability_analysis_settings: _Optional[int] = ..., consider_imperfection_case: bool = ..., generate_same_CO_without_IC: bool = ..., generate_co_without_initial_state: bool = ..., user_defined_action_combinations: bool = ..., favorable_permanent_actions: bool = ..., reduce_number_of_generated_combinations: bool = ..., auxiliary_combinations: bool = ..., generate_subcombinations_of_type_superposition: bool = ..., comment: _Optional[str] = ..., consider_initial_state: bool = ..., initial_state_items: _Optional[_Union[ArrayOfCombinationWizardInitialStateItems, _Mapping]] = ..., structure_modification_enabled: bool = ..., structure_modification: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfCombinationWizardInitialStateItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
