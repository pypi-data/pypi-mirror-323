from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConstructionStageGenerateCombinations(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONSTRUCTION_STAGE_GENERATE_COMBINATIONS_LOAD_COMBINATIONS: _ClassVar[ConstructionStageGenerateCombinations]
CONSTRUCTION_STAGE_GENERATE_COMBINATIONS_LOAD_COMBINATIONS: ConstructionStageGenerateCombinations

class ConstructionStage(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "to_solve", "continue_on_construction_stage", "start_time", "start_date", "end_time", "end_date", "duration", "loading", "generate_combinations", "static_analysis_settings", "consider_imperfection", "imperfection_case", "structure_modification_enabled", "structure_modification", "stability_analysis_enabled", "stability_analysis", "comment", "load_duration", "are_members_enabled_to_modify", "are_all_members_active", "added_members", "deactivated_members", "active_members", "member_property_modifications", "are_surfaces_enabled_to_modify", "are_all_surfaces_active", "added_surfaces", "deactivated_surfaces", "active_surfaces", "surface_property_modifications", "are_solids_enabled_to_modify", "are_all_solids_active", "added_solids", "deactivated_solids", "active_solids", "solid_property_modifications", "are_nodes_enabled_to_modify", "are_surface_contacts_enabled_to_modify", "are_all_surface_contacts_active", "added_surface_contacts", "deactivated_surface_contacts", "active_surface_contacts", "are_rigid_links_enabled_to_modify", "are_all_rigid_links_active", "added_rigid_links", "deactivated_rigid_links", "active_rigid_links", "support_all_nodes_with_support", "add_nodes_to_support", "deactivated_nodes_for_support", "currently_supported_nodes", "are_line_supports_enabled_to_modify", "support_all_lines_with_support", "add_lines_to_support", "deactivated_lines_for_support", "currently_supported_lines", "are_line_hinges_enabled_to_modify", "are_all_hinges_assigned", "add_line_hinges", "deactivated_line_hinges", "current_line_hinges", "are_line_welded_joints_enabled_to_modify", "are_all_welds_assigned", "add_line_welded_joints", "deactivated_line_welded_joints", "current_line_welded_joints", "geotechnical_analysis_reset_small_strain_history", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TO_SOLVE_FIELD_NUMBER: _ClassVar[int]
    CONTINUE_ON_CONSTRUCTION_STAGE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    GENERATE_COMBINATIONS_FIELD_NUMBER: _ClassVar[int]
    STATIC_ANALYSIS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_IMPERFECTION_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STRUCTURE_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    STABILITY_ANALYSIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STABILITY_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOAD_DURATION_FIELD_NUMBER: _ClassVar[int]
    ARE_MEMBERS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_MEMBERS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ADDED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PROPERTY_MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    ARE_SURFACES_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_SURFACES_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ADDED_SURFACES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SURFACES_FIELD_NUMBER: _ClassVar[int]
    SURFACE_PROPERTY_MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    ARE_SOLIDS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_SOLIDS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ADDED_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    SOLID_PROPERTY_MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    ARE_NODES_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_SURFACE_CONTACTS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_SURFACE_CONTACTS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ADDED_SURFACE_CONTACTS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_SURFACE_CONTACTS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_SURFACE_CONTACTS_FIELD_NUMBER: _ClassVar[int]
    ARE_RIGID_LINKS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_RIGID_LINKS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ADDED_RIGID_LINKS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_RIGID_LINKS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_RIGID_LINKS_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_ALL_NODES_WITH_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    ADD_NODES_TO_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_NODES_FOR_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    CURRENTLY_SUPPORTED_NODES_FIELD_NUMBER: _ClassVar[int]
    ARE_LINE_SUPPORTS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_ALL_LINES_WITH_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    ADD_LINES_TO_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_LINES_FOR_SUPPORT_FIELD_NUMBER: _ClassVar[int]
    CURRENTLY_SUPPORTED_LINES_FIELD_NUMBER: _ClassVar[int]
    ARE_LINE_HINGES_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_HINGES_ASSIGNED_FIELD_NUMBER: _ClassVar[int]
    ADD_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    ARE_LINE_WELDED_JOINTS_ENABLED_TO_MODIFY_FIELD_NUMBER: _ClassVar[int]
    ARE_ALL_WELDS_ASSIGNED_FIELD_NUMBER: _ClassVar[int]
    ADD_LINE_WELDED_JOINTS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATED_LINE_WELDED_JOINTS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LINE_WELDED_JOINTS_FIELD_NUMBER: _ClassVar[int]
    GEOTECHNICAL_ANALYSIS_RESET_SMALL_STRAIN_HISTORY_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    to_solve: bool
    continue_on_construction_stage: int
    start_time: float
    start_date: str
    end_time: float
    end_date: str
    duration: float
    loading: ArrayOfConstructionStageLoading
    generate_combinations: ConstructionStageGenerateCombinations
    static_analysis_settings: int
    consider_imperfection: bool
    imperfection_case: int
    structure_modification_enabled: bool
    structure_modification: int
    stability_analysis_enabled: bool
    stability_analysis: int
    comment: str
    load_duration: str
    are_members_enabled_to_modify: bool
    are_all_members_active: bool
    added_members: _containers.RepeatedScalarFieldContainer[int]
    deactivated_members: _containers.RepeatedScalarFieldContainer[int]
    active_members: _containers.RepeatedScalarFieldContainer[int]
    member_property_modifications: ArrayOfConstructionStageMemberPropertyModifications
    are_surfaces_enabled_to_modify: bool
    are_all_surfaces_active: bool
    added_surfaces: _containers.RepeatedScalarFieldContainer[int]
    deactivated_surfaces: _containers.RepeatedScalarFieldContainer[int]
    active_surfaces: _containers.RepeatedScalarFieldContainer[int]
    surface_property_modifications: ArrayOfConstructionStageSurfacePropertyModifications
    are_solids_enabled_to_modify: bool
    are_all_solids_active: bool
    added_solids: _containers.RepeatedScalarFieldContainer[int]
    deactivated_solids: _containers.RepeatedScalarFieldContainer[int]
    active_solids: _containers.RepeatedScalarFieldContainer[int]
    solid_property_modifications: ArrayOfConstructionStageSolidPropertyModifications
    are_nodes_enabled_to_modify: bool
    are_surface_contacts_enabled_to_modify: bool
    are_all_surface_contacts_active: bool
    added_surface_contacts: _containers.RepeatedScalarFieldContainer[int]
    deactivated_surface_contacts: _containers.RepeatedScalarFieldContainer[int]
    active_surface_contacts: _containers.RepeatedScalarFieldContainer[int]
    are_rigid_links_enabled_to_modify: bool
    are_all_rigid_links_active: bool
    added_rigid_links: _containers.RepeatedScalarFieldContainer[int]
    deactivated_rigid_links: _containers.RepeatedScalarFieldContainer[int]
    active_rigid_links: _containers.RepeatedScalarFieldContainer[int]
    support_all_nodes_with_support: bool
    add_nodes_to_support: _containers.RepeatedScalarFieldContainer[int]
    deactivated_nodes_for_support: _containers.RepeatedScalarFieldContainer[int]
    currently_supported_nodes: _containers.RepeatedScalarFieldContainer[int]
    are_line_supports_enabled_to_modify: bool
    support_all_lines_with_support: bool
    add_lines_to_support: _containers.RepeatedScalarFieldContainer[int]
    deactivated_lines_for_support: _containers.RepeatedScalarFieldContainer[int]
    currently_supported_lines: _containers.RepeatedScalarFieldContainer[int]
    are_line_hinges_enabled_to_modify: bool
    are_all_hinges_assigned: bool
    add_line_hinges: str
    deactivated_line_hinges: str
    current_line_hinges: str
    are_line_welded_joints_enabled_to_modify: bool
    are_all_welds_assigned: bool
    add_line_welded_joints: str
    deactivated_line_welded_joints: str
    current_line_welded_joints: str
    geotechnical_analysis_reset_small_strain_history: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., to_solve: bool = ..., continue_on_construction_stage: _Optional[int] = ..., start_time: _Optional[float] = ..., start_date: _Optional[str] = ..., end_time: _Optional[float] = ..., end_date: _Optional[str] = ..., duration: _Optional[float] = ..., loading: _Optional[_Union[ArrayOfConstructionStageLoading, _Mapping]] = ..., generate_combinations: _Optional[_Union[ConstructionStageGenerateCombinations, str]] = ..., static_analysis_settings: _Optional[int] = ..., consider_imperfection: bool = ..., imperfection_case: _Optional[int] = ..., structure_modification_enabled: bool = ..., structure_modification: _Optional[int] = ..., stability_analysis_enabled: bool = ..., stability_analysis: _Optional[int] = ..., comment: _Optional[str] = ..., load_duration: _Optional[str] = ..., are_members_enabled_to_modify: bool = ..., are_all_members_active: bool = ..., added_members: _Optional[_Iterable[int]] = ..., deactivated_members: _Optional[_Iterable[int]] = ..., active_members: _Optional[_Iterable[int]] = ..., member_property_modifications: _Optional[_Union[ArrayOfConstructionStageMemberPropertyModifications, _Mapping]] = ..., are_surfaces_enabled_to_modify: bool = ..., are_all_surfaces_active: bool = ..., added_surfaces: _Optional[_Iterable[int]] = ..., deactivated_surfaces: _Optional[_Iterable[int]] = ..., active_surfaces: _Optional[_Iterable[int]] = ..., surface_property_modifications: _Optional[_Union[ArrayOfConstructionStageSurfacePropertyModifications, _Mapping]] = ..., are_solids_enabled_to_modify: bool = ..., are_all_solids_active: bool = ..., added_solids: _Optional[_Iterable[int]] = ..., deactivated_solids: _Optional[_Iterable[int]] = ..., active_solids: _Optional[_Iterable[int]] = ..., solid_property_modifications: _Optional[_Union[ArrayOfConstructionStageSolidPropertyModifications, _Mapping]] = ..., are_nodes_enabled_to_modify: bool = ..., are_surface_contacts_enabled_to_modify: bool = ..., are_all_surface_contacts_active: bool = ..., added_surface_contacts: _Optional[_Iterable[int]] = ..., deactivated_surface_contacts: _Optional[_Iterable[int]] = ..., active_surface_contacts: _Optional[_Iterable[int]] = ..., are_rigid_links_enabled_to_modify: bool = ..., are_all_rigid_links_active: bool = ..., added_rigid_links: _Optional[_Iterable[int]] = ..., deactivated_rigid_links: _Optional[_Iterable[int]] = ..., active_rigid_links: _Optional[_Iterable[int]] = ..., support_all_nodes_with_support: bool = ..., add_nodes_to_support: _Optional[_Iterable[int]] = ..., deactivated_nodes_for_support: _Optional[_Iterable[int]] = ..., currently_supported_nodes: _Optional[_Iterable[int]] = ..., are_line_supports_enabled_to_modify: bool = ..., support_all_lines_with_support: bool = ..., add_lines_to_support: _Optional[_Iterable[int]] = ..., deactivated_lines_for_support: _Optional[_Iterable[int]] = ..., currently_supported_lines: _Optional[_Iterable[int]] = ..., are_line_hinges_enabled_to_modify: bool = ..., are_all_hinges_assigned: bool = ..., add_line_hinges: _Optional[str] = ..., deactivated_line_hinges: _Optional[str] = ..., current_line_hinges: _Optional[str] = ..., are_line_welded_joints_enabled_to_modify: bool = ..., are_all_welds_assigned: bool = ..., add_line_welded_joints: _Optional[str] = ..., deactivated_line_welded_joints: _Optional[str] = ..., current_line_welded_joints: _Optional[str] = ..., geotechnical_analysis_reset_small_strain_history: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfConstructionStageLoading(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConstructionStageMemberPropertyModifications(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConstructionStageSurfacePropertyModifications(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfConstructionStageSolidPropertyModifications(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
