from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StructureModification(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "assigned_to", "comment", "modify_stiffnesses_gamma_m", "modify_stiffnesses_materials", "modify_stiffnesses_sections", "modify_stiffnesses_members", "modify_stiffnesses_surfaces", "modify_stiffnesses_member_hinges", "modify_stiffnesses_line_hinges", "modify_stiffnesses_nodal_supports", "modify_stiffnesses_line_supports", "modify_stiffnesses_member_supports", "modify_stiffnesses_surface_supports", "modify_stiffness_member_reinforcement", "modify_stiffness_surface_reinforcement", "modify_stiffness_timber_members_due_moisture_class", "nonlinearities_disabled_material_nonlinearity_models", "nonlinearities_disabled_material_temperature_nonlinearities", "nonlinearities_disabled_line_hinges", "nonlinearities_disabled_member_types", "nonlinearities_disabled_member_hinges", "nonlinearities_disabled_member_nonlinearities", "nonlinearities_disabled_solid_types_contact_or_surfaces_contact", "nonlinearities_disabled_nodal_supports", "nonlinearities_disabled_line_supports", "nonlinearities_disabled_member_supports", "nonlinearities_disabled_surface_supports", "modify_stiffnesses_material_table", "modify_stiffnesses_section_table", "modify_stiffnesses_member_table", "modify_stiffnesses_surface_table", "modify_stiffnesses_member_hinges_table", "modify_stiffnesses_line_hinges_table", "modify_stiffnesses_nodal_supports_table", "modify_stiffnesses_line_supports_table", "modify_stiffnesses_member_supports_table", "modify_stiffnesses_surface_supports_table", "deactivate_members_enabled", "object_selection_for_deactivate_members", "deactivate_surfaces_enabled", "object_selection_for_deactivate_surfaces", "deactivate_solids_enabled", "object_selection_for_deactivate_solids", "deactivate_support_on_nodes_enabled", "object_selection_for_deactivate_support_on_nodes", "deactivate_support_on_lines_enabled", "object_selection_for_deactivate_support_on_lines", "deactivate_support_on_members_enabled", "object_selection_for_deactivate_support_on_members", "deactivate_support_on_surfaces_enabled", "object_selection_for_deactivate_support_on_surfaces", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_GAMMA_M_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MATERIALS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SECTIONS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_HINGES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_MEMBER_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_SURFACE_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESS_TIMBER_MEMBERS_DUE_MOISTURE_CLASS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MATERIAL_NONLINEARITY_MODELS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MATERIAL_TEMPERATURE_NONLINEARITIES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_LINE_HINGES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_TYPES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_HINGES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_NONLINEARITIES_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_SOLID_TYPES_CONTACT_OR_SURFACES_CONTACT_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_NODAL_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_LINE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_MEMBER_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    NONLINEARITIES_DISABLED_SURFACE_SUPPORTS_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MATERIAL_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SECTION_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_HINGES_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_HINGES_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_NODAL_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_LINE_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_MEMBER_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    MODIFY_STIFFNESSES_SURFACE_SUPPORTS_TABLE_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_MEMBERS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SURFACES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SOLIDS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_NODES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_NODES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_LINES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_LINES_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_MEMBERS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEACTIVATE_SUPPORT_ON_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SELECTION_FOR_DEACTIVATE_SUPPORT_ON_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    assigned_to: str
    comment: str
    modify_stiffnesses_gamma_m: bool
    modify_stiffnesses_materials: bool
    modify_stiffnesses_sections: bool
    modify_stiffnesses_members: bool
    modify_stiffnesses_surfaces: bool
    modify_stiffnesses_member_hinges: bool
    modify_stiffnesses_line_hinges: bool
    modify_stiffnesses_nodal_supports: bool
    modify_stiffnesses_line_supports: bool
    modify_stiffnesses_member_supports: bool
    modify_stiffnesses_surface_supports: bool
    modify_stiffness_member_reinforcement: bool
    modify_stiffness_surface_reinforcement: bool
    modify_stiffness_timber_members_due_moisture_class: bool
    nonlinearities_disabled_material_nonlinearity_models: bool
    nonlinearities_disabled_material_temperature_nonlinearities: bool
    nonlinearities_disabled_line_hinges: bool
    nonlinearities_disabled_member_types: bool
    nonlinearities_disabled_member_hinges: bool
    nonlinearities_disabled_member_nonlinearities: bool
    nonlinearities_disabled_solid_types_contact_or_surfaces_contact: bool
    nonlinearities_disabled_nodal_supports: bool
    nonlinearities_disabled_line_supports: bool
    nonlinearities_disabled_member_supports: bool
    nonlinearities_disabled_surface_supports: bool
    modify_stiffnesses_material_table: ArrayOfStructureModificationModifyStiffnessesMaterialTable
    modify_stiffnesses_section_table: ArrayOfStructureModificationModifyStiffnessesSectionTable
    modify_stiffnesses_member_table: ArrayOfStructureModificationModifyStiffnessesMemberTable
    modify_stiffnesses_surface_table: ArrayOfStructureModificationModifyStiffnessesSurfaceTable
    modify_stiffnesses_member_hinges_table: ArrayOfStructureModificationModifyStiffnessesMemberHingesTable
    modify_stiffnesses_line_hinges_table: ArrayOfStructureModificationModifyStiffnessesLineHingesTable
    modify_stiffnesses_nodal_supports_table: ArrayOfStructureModificationModifyStiffnessesNodalSupportsTable
    modify_stiffnesses_line_supports_table: ArrayOfStructureModificationModifyStiffnessesLineSupportsTable
    modify_stiffnesses_member_supports_table: ArrayOfStructureModificationModifyStiffnessesMemberSupportsTable
    modify_stiffnesses_surface_supports_table: ArrayOfStructureModificationModifyStiffnessesSurfaceSupportsTable
    deactivate_members_enabled: bool
    object_selection_for_deactivate_members: int
    deactivate_surfaces_enabled: bool
    object_selection_for_deactivate_surfaces: int
    deactivate_solids_enabled: bool
    object_selection_for_deactivate_solids: int
    deactivate_support_on_nodes_enabled: bool
    object_selection_for_deactivate_support_on_nodes: int
    deactivate_support_on_lines_enabled: bool
    object_selection_for_deactivate_support_on_lines: int
    deactivate_support_on_members_enabled: bool
    object_selection_for_deactivate_support_on_members: int
    deactivate_support_on_surfaces_enabled: bool
    object_selection_for_deactivate_support_on_surfaces: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., assigned_to: _Optional[str] = ..., comment: _Optional[str] = ..., modify_stiffnesses_gamma_m: bool = ..., modify_stiffnesses_materials: bool = ..., modify_stiffnesses_sections: bool = ..., modify_stiffnesses_members: bool = ..., modify_stiffnesses_surfaces: bool = ..., modify_stiffnesses_member_hinges: bool = ..., modify_stiffnesses_line_hinges: bool = ..., modify_stiffnesses_nodal_supports: bool = ..., modify_stiffnesses_line_supports: bool = ..., modify_stiffnesses_member_supports: bool = ..., modify_stiffnesses_surface_supports: bool = ..., modify_stiffness_member_reinforcement: bool = ..., modify_stiffness_surface_reinforcement: bool = ..., modify_stiffness_timber_members_due_moisture_class: bool = ..., nonlinearities_disabled_material_nonlinearity_models: bool = ..., nonlinearities_disabled_material_temperature_nonlinearities: bool = ..., nonlinearities_disabled_line_hinges: bool = ..., nonlinearities_disabled_member_types: bool = ..., nonlinearities_disabled_member_hinges: bool = ..., nonlinearities_disabled_member_nonlinearities: bool = ..., nonlinearities_disabled_solid_types_contact_or_surfaces_contact: bool = ..., nonlinearities_disabled_nodal_supports: bool = ..., nonlinearities_disabled_line_supports: bool = ..., nonlinearities_disabled_member_supports: bool = ..., nonlinearities_disabled_surface_supports: bool = ..., modify_stiffnesses_material_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesMaterialTable, _Mapping]] = ..., modify_stiffnesses_section_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesSectionTable, _Mapping]] = ..., modify_stiffnesses_member_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesMemberTable, _Mapping]] = ..., modify_stiffnesses_surface_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesSurfaceTable, _Mapping]] = ..., modify_stiffnesses_member_hinges_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesMemberHingesTable, _Mapping]] = ..., modify_stiffnesses_line_hinges_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesLineHingesTable, _Mapping]] = ..., modify_stiffnesses_nodal_supports_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesNodalSupportsTable, _Mapping]] = ..., modify_stiffnesses_line_supports_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesLineSupportsTable, _Mapping]] = ..., modify_stiffnesses_member_supports_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesMemberSupportsTable, _Mapping]] = ..., modify_stiffnesses_surface_supports_table: _Optional[_Union[ArrayOfStructureModificationModifyStiffnessesSurfaceSupportsTable, _Mapping]] = ..., deactivate_members_enabled: bool = ..., object_selection_for_deactivate_members: _Optional[int] = ..., deactivate_surfaces_enabled: bool = ..., object_selection_for_deactivate_surfaces: _Optional[int] = ..., deactivate_solids_enabled: bool = ..., object_selection_for_deactivate_solids: _Optional[int] = ..., deactivate_support_on_nodes_enabled: bool = ..., object_selection_for_deactivate_support_on_nodes: _Optional[int] = ..., deactivate_support_on_lines_enabled: bool = ..., object_selection_for_deactivate_support_on_lines: _Optional[int] = ..., deactivate_support_on_members_enabled: bool = ..., object_selection_for_deactivate_support_on_members: _Optional[int] = ..., deactivate_support_on_surfaces_enabled: bool = ..., object_selection_for_deactivate_support_on_surfaces: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesMaterialTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesSectionTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesMemberTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesSurfaceTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesMemberHingesTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesLineHingesTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesNodalSupportsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesLineSupportsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesMemberSupportsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfStructureModificationModifyStiffnessesSurfaceSupportsTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
