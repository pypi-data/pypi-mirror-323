from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberSetSetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_SET_SET_TYPE_CONTINUOUS: _ClassVar[MemberSetSetType]
    MEMBER_SET_SET_TYPE_GROUP: _ClassVar[MemberSetSetType]

class MemberSetDeflectionCheckDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Y: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z_AND_Y: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Y: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z_AND_Y: _ClassVar[MemberSetDeflectionCheckDirection]
    MEMBER_SET_DEFLECTION_CHECK_DIRECTION_RESULTING_AXIS: _ClassVar[MemberSetDeflectionCheckDirection]

class MemberSetDeflectionCheckDisplacementReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_SET_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_SEGMENT_ENDS: _ClassVar[MemberSetDeflectionCheckDisplacementReference]
    MEMBER_SET_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_UNDEFORMED_SYSTEM: _ClassVar[MemberSetDeflectionCheckDisplacementReference]
MEMBER_SET_SET_TYPE_CONTINUOUS: MemberSetSetType
MEMBER_SET_SET_TYPE_GROUP: MemberSetSetType
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Y: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z_AND_Y: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Y: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z_AND_Y: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DIRECTION_RESULTING_AXIS: MemberSetDeflectionCheckDirection
MEMBER_SET_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_SEGMENT_ENDS: MemberSetDeflectionCheckDisplacementReference
MEMBER_SET_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_UNDEFORMED_SYSTEM: MemberSetDeflectionCheckDisplacementReference

class MemberSet(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "set_type", "length", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "position", "position_short", "comment", "is_generated", "generating_object_info", "volume", "mass", "member_set_representative", "discontinuous_torsional_warping", "steel_effective_lengths", "steel_boundary_conditions", "steel_member_local_section_reductions", "member_steel_design_uls_configuration", "member_steel_design_sls_configuration", "member_steel_design_fr_configuration", "member_steel_design_seismic_configuration", "aluminum_effective_lengths", "aluminum_boundary_conditions", "aluminum_member_local_section_reductions", "aluminum_member_transverse_weld", "member_aluminum_design_uls_configuration", "member_aluminum_design_sls_configuration", "member_set_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled", "concrete_shear_reinforcement_spans", "concrete_longitudinal_reinforcement_items", "concrete_cover_user_defined_enabled", "concrete_cover_different_at_section_sides_enabled", "concrete_cover", "concrete_cover_top", "concrete_cover_bottom", "concrete_cover_left", "concrete_cover_right", "concrete_cover_min", "concrete_cover_min_top", "concrete_cover_min_bottom", "concrete_cover_min_left", "concrete_cover_min_right", "concrete_durability", "concrete_durability_top", "concrete_durability_bottom", "concrete_durability_left", "concrete_durability_right", "concrete_effective_lengths", "member_concrete_design_uls_configuration", "member_concrete_design_sls_configuration", "member_concrete_design_fr_configuration", "member_concrete_design_seismic_configuration", "timber_effective_lengths", "service_class_timber_design", "moisture_class_timber_design", "service_conditions_timber_design", "timber_local_section_reductions", "member_timber_design_fr_configuration", "member_timber_design_sls_configuration", "member_timber_design_uls_configuration", "support", "member_transverse_stiffener", "member_openings", "stress_analysis_configuration", "deflection_check_direction", "deflection_check_displacement_reference", "design_support_on_member_set_start", "design_support_on_member_set_end", "design_supports_on_internal_nodes", "members", "deflection_segments_defined_length_y_axis_enabled", "deflection_segments_defined_length_z_axis_enabled", "deflection_segments_y_axis", "deflection_segments_z_axis", "design_properties_activated", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SET_TYPE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    POSITION_SHORT_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SET_REPRESENTATIVE_FIELD_NUMBER: _ClassVar[int]
    DISCONTINUOUS_TORSIONAL_WARPING_FIELD_NUMBER: _ClassVar[int]
    STEEL_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STEEL_BOUNDARY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    STEEL_MEMBER_LOCAL_SECTION_REDUCTIONS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_SEISMIC_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_BOUNDARY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_MEMBER_LOCAL_SECTION_REDUCTIONS_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_MEMBER_TRANSVERSE_WELD_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ALUMINUM_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ALUMINUM_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SET_RIB_GENERATING_LONGITUDINAL_REINFORCEMENT_ITEMS_FROM_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_SHEAR_REINFORCEMENT_SPANS_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_LONGITUDINAL_REINFORCEMENT_ITEMS_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_USER_DEFINED_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_DIFFERENT_AT_SECTION_SIDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_SEISMIC_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    TIMBER_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CLASS_TIMBER_DESIGN_FIELD_NUMBER: _ClassVar[int]
    MOISTURE_CLASS_TIMBER_DESIGN_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CONDITIONS_TIMBER_DESIGN_FIELD_NUMBER: _ClassVar[int]
    TIMBER_LOCAL_SECTION_REDUCTIONS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TRANSVERSE_STIFFENER_FIELD_NUMBER: _ClassVar[int]
    MEMBER_OPENINGS_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORT_ON_MEMBER_SET_START_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORT_ON_MEMBER_SET_END_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORTS_ON_INTERNAL_NODES_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_DEFINED_LENGTH_Y_AXIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_DEFINED_LENGTH_Z_AXIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_Y_AXIS_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_Z_AXIS_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    set_type: MemberSetSetType
    length: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    position: str
    position_short: str
    comment: str
    is_generated: bool
    generating_object_info: str
    volume: float
    mass: float
    member_set_representative: int
    discontinuous_torsional_warping: bool
    steel_effective_lengths: int
    steel_boundary_conditions: int
    steel_member_local_section_reductions: int
    member_steel_design_uls_configuration: int
    member_steel_design_sls_configuration: int
    member_steel_design_fr_configuration: int
    member_steel_design_seismic_configuration: int
    aluminum_effective_lengths: int
    aluminum_boundary_conditions: int
    aluminum_member_local_section_reductions: int
    aluminum_member_transverse_weld: int
    member_aluminum_design_uls_configuration: int
    member_aluminum_design_sls_configuration: int
    member_set_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled: bool
    concrete_shear_reinforcement_spans: ArrayOfMemberSetConcreteShearReinforcementSpans
    concrete_longitudinal_reinforcement_items: ArrayOfMemberSetConcreteLongitudinalReinforcementItems
    concrete_cover_user_defined_enabled: bool
    concrete_cover_different_at_section_sides_enabled: bool
    concrete_cover: float
    concrete_cover_top: float
    concrete_cover_bottom: float
    concrete_cover_left: float
    concrete_cover_right: float
    concrete_cover_min: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_top: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_bottom: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_left: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_right: _containers.RepeatedScalarFieldContainer[int]
    concrete_durability: int
    concrete_durability_top: int
    concrete_durability_bottom: int
    concrete_durability_left: int
    concrete_durability_right: int
    concrete_effective_lengths: int
    member_concrete_design_uls_configuration: int
    member_concrete_design_sls_configuration: int
    member_concrete_design_fr_configuration: int
    member_concrete_design_seismic_configuration: int
    timber_effective_lengths: int
    service_class_timber_design: int
    moisture_class_timber_design: int
    service_conditions_timber_design: int
    timber_local_section_reductions: int
    member_timber_design_fr_configuration: int
    member_timber_design_sls_configuration: int
    member_timber_design_uls_configuration: int
    support: int
    member_transverse_stiffener: int
    member_openings: int
    stress_analysis_configuration: int
    deflection_check_direction: MemberSetDeflectionCheckDirection
    deflection_check_displacement_reference: MemberSetDeflectionCheckDisplacementReference
    design_support_on_member_set_start: int
    design_support_on_member_set_end: int
    design_supports_on_internal_nodes: ArrayOfMemberSetDesignSupportsOnInternalNodes
    members: _containers.RepeatedScalarFieldContainer[int]
    deflection_segments_defined_length_y_axis_enabled: bool
    deflection_segments_defined_length_z_axis_enabled: bool
    deflection_segments_y_axis: ArrayOfMemberSetDeflectionSegmentsYAxis
    deflection_segments_z_axis: ArrayOfMemberSetDeflectionSegmentsZAxis
    design_properties_activated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., set_type: _Optional[_Union[MemberSetSetType, str]] = ..., length: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., position: _Optional[str] = ..., position_short: _Optional[str] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., volume: _Optional[float] = ..., mass: _Optional[float] = ..., member_set_representative: _Optional[int] = ..., discontinuous_torsional_warping: bool = ..., steel_effective_lengths: _Optional[int] = ..., steel_boundary_conditions: _Optional[int] = ..., steel_member_local_section_reductions: _Optional[int] = ..., member_steel_design_uls_configuration: _Optional[int] = ..., member_steel_design_sls_configuration: _Optional[int] = ..., member_steel_design_fr_configuration: _Optional[int] = ..., member_steel_design_seismic_configuration: _Optional[int] = ..., aluminum_effective_lengths: _Optional[int] = ..., aluminum_boundary_conditions: _Optional[int] = ..., aluminum_member_local_section_reductions: _Optional[int] = ..., aluminum_member_transverse_weld: _Optional[int] = ..., member_aluminum_design_uls_configuration: _Optional[int] = ..., member_aluminum_design_sls_configuration: _Optional[int] = ..., member_set_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled: bool = ..., concrete_shear_reinforcement_spans: _Optional[_Union[ArrayOfMemberSetConcreteShearReinforcementSpans, _Mapping]] = ..., concrete_longitudinal_reinforcement_items: _Optional[_Union[ArrayOfMemberSetConcreteLongitudinalReinforcementItems, _Mapping]] = ..., concrete_cover_user_defined_enabled: bool = ..., concrete_cover_different_at_section_sides_enabled: bool = ..., concrete_cover: _Optional[float] = ..., concrete_cover_top: _Optional[float] = ..., concrete_cover_bottom: _Optional[float] = ..., concrete_cover_left: _Optional[float] = ..., concrete_cover_right: _Optional[float] = ..., concrete_cover_min: _Optional[_Iterable[int]] = ..., concrete_cover_min_top: _Optional[_Iterable[int]] = ..., concrete_cover_min_bottom: _Optional[_Iterable[int]] = ..., concrete_cover_min_left: _Optional[_Iterable[int]] = ..., concrete_cover_min_right: _Optional[_Iterable[int]] = ..., concrete_durability: _Optional[int] = ..., concrete_durability_top: _Optional[int] = ..., concrete_durability_bottom: _Optional[int] = ..., concrete_durability_left: _Optional[int] = ..., concrete_durability_right: _Optional[int] = ..., concrete_effective_lengths: _Optional[int] = ..., member_concrete_design_uls_configuration: _Optional[int] = ..., member_concrete_design_sls_configuration: _Optional[int] = ..., member_concrete_design_fr_configuration: _Optional[int] = ..., member_concrete_design_seismic_configuration: _Optional[int] = ..., timber_effective_lengths: _Optional[int] = ..., service_class_timber_design: _Optional[int] = ..., moisture_class_timber_design: _Optional[int] = ..., service_conditions_timber_design: _Optional[int] = ..., timber_local_section_reductions: _Optional[int] = ..., member_timber_design_fr_configuration: _Optional[int] = ..., member_timber_design_sls_configuration: _Optional[int] = ..., member_timber_design_uls_configuration: _Optional[int] = ..., support: _Optional[int] = ..., member_transverse_stiffener: _Optional[int] = ..., member_openings: _Optional[int] = ..., stress_analysis_configuration: _Optional[int] = ..., deflection_check_direction: _Optional[_Union[MemberSetDeflectionCheckDirection, str]] = ..., deflection_check_displacement_reference: _Optional[_Union[MemberSetDeflectionCheckDisplacementReference, str]] = ..., design_support_on_member_set_start: _Optional[int] = ..., design_support_on_member_set_end: _Optional[int] = ..., design_supports_on_internal_nodes: _Optional[_Union[ArrayOfMemberSetDesignSupportsOnInternalNodes, _Mapping]] = ..., members: _Optional[_Iterable[int]] = ..., deflection_segments_defined_length_y_axis_enabled: bool = ..., deflection_segments_defined_length_z_axis_enabled: bool = ..., deflection_segments_y_axis: _Optional[_Union[ArrayOfMemberSetDeflectionSegmentsYAxis, _Mapping]] = ..., deflection_segments_z_axis: _Optional[_Union[ArrayOfMemberSetDeflectionSegmentsZAxis, _Mapping]] = ..., design_properties_activated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfMemberSetConcreteShearReinforcementSpans(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberSetConcreteLongitudinalReinforcementItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberSetDesignSupportsOnInternalNodes(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberSetDeflectionSegmentsYAxis(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberSetDeflectionSegmentsZAxis(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
