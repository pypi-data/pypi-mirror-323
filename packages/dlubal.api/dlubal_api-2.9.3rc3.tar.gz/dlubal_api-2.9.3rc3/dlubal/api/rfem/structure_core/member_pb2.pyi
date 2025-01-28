from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_TYPE_UNKNOWN: _ClassVar[MemberType]
    MEMBER_TYPE_BEAM: _ClassVar[MemberType]
    MEMBER_TYPE_BUCKLING: _ClassVar[MemberType]
    MEMBER_TYPE_CABLE: _ClassVar[MemberType]
    MEMBER_TYPE_COMPRESSION: _ClassVar[MemberType]
    MEMBER_TYPE_COUPLING_HINGE_HINGE: _ClassVar[MemberType]
    MEMBER_TYPE_COUPLING_HINGE_RIGID: _ClassVar[MemberType]
    MEMBER_TYPE_COUPLING_RIGID_HINGE: _ClassVar[MemberType]
    MEMBER_TYPE_COUPLING_RIGID_RIGID: _ClassVar[MemberType]
    MEMBER_TYPE_DAMPER: _ClassVar[MemberType]
    MEMBER_TYPE_DEFINABLE_STIFFNESS: _ClassVar[MemberType]
    MEMBER_TYPE_JOIST: _ClassVar[MemberType]
    MEMBER_TYPE_PILE: _ClassVar[MemberType]
    MEMBER_TYPE_RESULT_BEAM: _ClassVar[MemberType]
    MEMBER_TYPE_RESULT_LINE: _ClassVar[MemberType]
    MEMBER_TYPE_RIB: _ClassVar[MemberType]
    MEMBER_TYPE_RIGID: _ClassVar[MemberType]
    MEMBER_TYPE_SPRING: _ClassVar[MemberType]
    MEMBER_TYPE_SURFACE_MODEL: _ClassVar[MemberType]
    MEMBER_TYPE_TENSION: _ClassVar[MemberType]
    MEMBER_TYPE_TRUSS: _ClassVar[MemberType]
    MEMBER_TYPE_TRUSS_ONLY_N: _ClassVar[MemberType]

class MemberSectionDistributionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_SECTION_DISTRIBUTION_TYPE_UNIFORM: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_CURVED: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_FISH_BEAM_PARABOLIC: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_LINEAR: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_NONE: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_BOTH_SIDES: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_END_OF_MEMBER: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_START_OF_MEMBER: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_PITCHED_CAMBERED_BEAM_WITH_CONSTANT_HEIGHT: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_PITCHED_CAMBERED_BEAM_WITH_VARIABLE_HEIGHT: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_SADDLE: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_BOTH_SIDES: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_END_OF_MEMBER: _ClassVar[MemberSectionDistributionType]
    MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_START_OF_MEMBER: _ClassVar[MemberSectionDistributionType]

class MemberReferenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_REFERENCE_TYPE_L: _ClassVar[MemberReferenceType]
    MEMBER_REFERENCE_TYPE_XY: _ClassVar[MemberReferenceType]
    MEMBER_REFERENCE_TYPE_XZ: _ClassVar[MemberReferenceType]
    MEMBER_REFERENCE_TYPE_YZ: _ClassVar[MemberReferenceType]

class MemberMemberTypeRibAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_ON_Z_SIDE_NEGATIVE: _ClassVar[MemberMemberTypeRibAlignment]
    MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_CENTRIC: _ClassVar[MemberMemberTypeRibAlignment]
    MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_ON_Z_SIDE_POSITIVE: _ClassVar[MemberMemberTypeRibAlignment]
    MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_USER_DEFINED_VIA_MEMBER_ECCENTRICITY: _ClassVar[MemberMemberTypeRibAlignment]

class MemberMemberRibSurfaceRoughnessClassification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_INDENTED: _ClassVar[MemberMemberRibSurfaceRoughnessClassification]
    MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_ROUGH: _ClassVar[MemberMemberRibSurfaceRoughnessClassification]
    MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_SMOOTH: _ClassVar[MemberMemberRibSurfaceRoughnessClassification]
    MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_VERY_SMOOTH: _ClassVar[MemberMemberRibSurfaceRoughnessClassification]

class MemberResultBeamIntegrateStressesAndForces(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CUBOID_QUADRATIC: _ClassVar[MemberResultBeamIntegrateStressesAndForces]
    MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_FROM_LISTED_INCLUDE_OBJECTS: _ClassVar[MemberResultBeamIntegrateStressesAndForces]
    MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CUBOID_GENERAL: _ClassVar[MemberResultBeamIntegrateStressesAndForces]
    MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CYLINDER: _ClassVar[MemberResultBeamIntegrateStressesAndForces]

class MemberSectionAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_SECTION_ALIGNMENT_TOP: _ClassVar[MemberSectionAlignment]
    MEMBER_SECTION_ALIGNMENT_BOTTOM: _ClassVar[MemberSectionAlignment]
    MEMBER_SECTION_ALIGNMENT_CENTRIC: _ClassVar[MemberSectionAlignment]

class MemberGrainAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_GRAIN_ALIGNMENT_TOP: _ClassVar[MemberGrainAlignment]
    MEMBER_GRAIN_ALIGNMENT_BOTTOM: _ClassVar[MemberGrainAlignment]
    MEMBER_GRAIN_ALIGNMENT_CENTRIC: _ClassVar[MemberGrainAlignment]

class MemberCurvedMemberCantileversType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_HORIZONTAL: _ClassVar[MemberCurvedMemberCantileversType]
    MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_OFFSET: _ClassVar[MemberCurvedMemberCantileversType]
    MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_PARALLEL: _ClassVar[MemberCurvedMemberCantileversType]
    MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_TAPER: _ClassVar[MemberCurvedMemberCantileversType]

class MemberRotationSpecificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_ROTATION_SPECIFICATION_TYPE_BY_ANGLE: _ClassVar[MemberRotationSpecificationType]
    MEMBER_ROTATION_SPECIFICATION_TYPE_INSIDE: _ClassVar[MemberRotationSpecificationType]
    MEMBER_ROTATION_SPECIFICATION_TYPE_SURFACE: _ClassVar[MemberRotationSpecificationType]
    MEMBER_ROTATION_SPECIFICATION_TYPE_TO_NODE: _ClassVar[MemberRotationSpecificationType]

class MemberRotationPlaneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_ROTATION_PLANE_TYPE_ROTATION_PLANE_XY: _ClassVar[MemberRotationPlaneType]
    MEMBER_ROTATION_PLANE_TYPE_ROTATION_PLANE_XZ: _ClassVar[MemberRotationPlaneType]

class MemberRotationSurfacePlaneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XY: _ClassVar[MemberRotationSurfacePlaneType]
    MEMBER_ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XZ: _ClassVar[MemberRotationSurfacePlaneType]

class MemberDeflectionCheckDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Y: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z_AND_Y: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Y: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z_AND_Y: _ClassVar[MemberDeflectionCheckDirection]
    MEMBER_DEFLECTION_CHECK_DIRECTION_RESULTING_AXIS: _ClassVar[MemberDeflectionCheckDirection]

class MemberDeflectionCheckDisplacementReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEMBER_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_SEGMENT_ENDS: _ClassVar[MemberDeflectionCheckDisplacementReference]
    MEMBER_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_UNDEFORMED_SYSTEM: _ClassVar[MemberDeflectionCheckDisplacementReference]
MEMBER_TYPE_UNKNOWN: MemberType
MEMBER_TYPE_BEAM: MemberType
MEMBER_TYPE_BUCKLING: MemberType
MEMBER_TYPE_CABLE: MemberType
MEMBER_TYPE_COMPRESSION: MemberType
MEMBER_TYPE_COUPLING_HINGE_HINGE: MemberType
MEMBER_TYPE_COUPLING_HINGE_RIGID: MemberType
MEMBER_TYPE_COUPLING_RIGID_HINGE: MemberType
MEMBER_TYPE_COUPLING_RIGID_RIGID: MemberType
MEMBER_TYPE_DAMPER: MemberType
MEMBER_TYPE_DEFINABLE_STIFFNESS: MemberType
MEMBER_TYPE_JOIST: MemberType
MEMBER_TYPE_PILE: MemberType
MEMBER_TYPE_RESULT_BEAM: MemberType
MEMBER_TYPE_RESULT_LINE: MemberType
MEMBER_TYPE_RIB: MemberType
MEMBER_TYPE_RIGID: MemberType
MEMBER_TYPE_SPRING: MemberType
MEMBER_TYPE_SURFACE_MODEL: MemberType
MEMBER_TYPE_TENSION: MemberType
MEMBER_TYPE_TRUSS: MemberType
MEMBER_TYPE_TRUSS_ONLY_N: MemberType
MEMBER_SECTION_DISTRIBUTION_TYPE_UNIFORM: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_CURVED: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_FISH_BEAM_PARABOLIC: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_LINEAR: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_NONE: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_BOTH_SIDES: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_END_OF_MEMBER: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_OFFSET_AT_START_OF_MEMBER: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_PITCHED_CAMBERED_BEAM_WITH_CONSTANT_HEIGHT: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_PITCHED_CAMBERED_BEAM_WITH_VARIABLE_HEIGHT: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_SADDLE: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_BOTH_SIDES: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_END_OF_MEMBER: MemberSectionDistributionType
MEMBER_SECTION_DISTRIBUTION_TYPE_TAPERED_AT_START_OF_MEMBER: MemberSectionDistributionType
MEMBER_REFERENCE_TYPE_L: MemberReferenceType
MEMBER_REFERENCE_TYPE_XY: MemberReferenceType
MEMBER_REFERENCE_TYPE_XZ: MemberReferenceType
MEMBER_REFERENCE_TYPE_YZ: MemberReferenceType
MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_ON_Z_SIDE_NEGATIVE: MemberMemberTypeRibAlignment
MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_CENTRIC: MemberMemberTypeRibAlignment
MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_ON_Z_SIDE_POSITIVE: MemberMemberTypeRibAlignment
MEMBER_MEMBER_TYPE_RIB_ALIGNMENT_USER_DEFINED_VIA_MEMBER_ECCENTRICITY: MemberMemberTypeRibAlignment
MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_INDENTED: MemberMemberRibSurfaceRoughnessClassification
MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_ROUGH: MemberMemberRibSurfaceRoughnessClassification
MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_SMOOTH: MemberMemberRibSurfaceRoughnessClassification
MEMBER_MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_VERY_SMOOTH: MemberMemberRibSurfaceRoughnessClassification
MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CUBOID_QUADRATIC: MemberResultBeamIntegrateStressesAndForces
MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_FROM_LISTED_INCLUDE_OBJECTS: MemberResultBeamIntegrateStressesAndForces
MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CUBOID_GENERAL: MemberResultBeamIntegrateStressesAndForces
MEMBER_RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_WITHIN_CYLINDER: MemberResultBeamIntegrateStressesAndForces
MEMBER_SECTION_ALIGNMENT_TOP: MemberSectionAlignment
MEMBER_SECTION_ALIGNMENT_BOTTOM: MemberSectionAlignment
MEMBER_SECTION_ALIGNMENT_CENTRIC: MemberSectionAlignment
MEMBER_GRAIN_ALIGNMENT_TOP: MemberGrainAlignment
MEMBER_GRAIN_ALIGNMENT_BOTTOM: MemberGrainAlignment
MEMBER_GRAIN_ALIGNMENT_CENTRIC: MemberGrainAlignment
MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_HORIZONTAL: MemberCurvedMemberCantileversType
MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_OFFSET: MemberCurvedMemberCantileversType
MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_PARALLEL: MemberCurvedMemberCantileversType
MEMBER_CURVED_MEMBER_CANTILEVERS_TYPE_TAPER: MemberCurvedMemberCantileversType
MEMBER_ROTATION_SPECIFICATION_TYPE_BY_ANGLE: MemberRotationSpecificationType
MEMBER_ROTATION_SPECIFICATION_TYPE_INSIDE: MemberRotationSpecificationType
MEMBER_ROTATION_SPECIFICATION_TYPE_SURFACE: MemberRotationSpecificationType
MEMBER_ROTATION_SPECIFICATION_TYPE_TO_NODE: MemberRotationSpecificationType
MEMBER_ROTATION_PLANE_TYPE_ROTATION_PLANE_XY: MemberRotationPlaneType
MEMBER_ROTATION_PLANE_TYPE_ROTATION_PLANE_XZ: MemberRotationPlaneType
MEMBER_ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XY: MemberRotationSurfacePlaneType
MEMBER_ROTATION_SURFACE_PLANE_TYPE_ROTATION_PLANE_XZ: MemberRotationSurfacePlaneType
MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Y: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_AUXILIARY_LOCAL_AXIS_Z_AND_Y: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Y: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_LOCAL_AXIS_Z_AND_Y: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DIRECTION_RESULTING_AXIS: MemberDeflectionCheckDirection
MEMBER_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_SEGMENT_ENDS: MemberDeflectionCheckDisplacementReference
MEMBER_DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_DEFORMED_UNDEFORMED_SYSTEM: MemberDeflectionCheckDisplacementReference

class Member(_message.Message):
    __slots__ = ("no", "type", "is_deactivated_for_calculation", "line", "section_distribution_type", "reference_type", "nodes", "node_start", "node_end", "analytical_length", "analytical_volume", "analytical_surface_of_coating", "analytical_mass", "surface_of_coating", "analytical_center_of_gravity", "analytical_center_of_gravity_x", "analytical_center_of_gravity_y", "analytical_center_of_gravity_z", "length", "volume", "mass", "center_of_gravity", "center_of_gravity_x", "center_of_gravity_y", "center_of_gravity_z", "member_representative", "design_properties_via_member", "design_properties_via_parent_member_set", "design_properties_parent_member_set", "comment", "member_type_rib_alignment", "member_rib_first_surface", "member_rib_second_surface", "member_rib_surface_assignment_autodetect", "align_local_z_axis_to_local_z_axis_of_surface", "member_rib_shear_joint_between_web_and_flange", "member_rib_surface_roughness_classification", "member_rib_reduction_of_joint_width", "flange_dimensions", "synchronize_width_mode", "relative_ordinates_mode", "member_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled", "member_type_definable_stiffness", "result_beam_integrate_stresses_and_forces", "result_beam_y_z", "result_beam_y_plus", "result_beam_z_plus", "result_beam_y_minus", "result_beam_z_minus", "result_beam_radius", "result_beam_include_all_surfaces", "result_beam_include_surfaces", "result_beam_include_all_solids", "result_beam_include_solids", "result_beam_include_all_members", "result_beam_include_members", "result_beam_exclude_surfaces", "result_beam_exclude_solids", "result_beam_exclude_members", "projected_length", "section_distance_from_start_is_defined_as_relative", "section_distance_from_start_absolute", "section_distance_from_start_relative", "section_distance_from_end_is_defined_as_relative", "section_distance_from_end_absolute", "section_distance_from_end_relative", "section_alignment", "section_start", "section_end", "section_internal", "section_material", "grain_alignment", "is_curved", "curved_member_is_asymmetric_layout", "curved_member_is_cantilevers", "curved_member_cantilevers_type", "curved_member_is_capped_with_loose_ridge_wedge", "curved_member_parameters", "rotation_specification_type", "rotation_angle", "rotation_help_node", "rotation_plane_type", "rotation_surface", "rotation_surface_plane_type", "is_rotated", "member_hinge_start", "member_hinge_end", "member_eccentricity_start", "member_eccentricity_end", "support", "member_transverse_stiffener", "member_openings", "member_nonlinearity", "member_result_intermediate_point", "stress_analysis_configuration", "aluminum_effective_lengths", "aluminum_boundary_conditions", "aluminum_member_local_section_reduction", "aluminum_member_transverse_weld", "member_aluminum_design_uls_configuration", "member_aluminum_design_sls_configuration", "concrete_effective_lengths", "concrete_cover_user_defined_enabled", "concrete_cover", "concrete_cover_top", "concrete_cover_left", "concrete_cover_right", "concrete_cover_bottom", "concrete_cover_min", "concrete_cover_min_top", "concrete_cover_min_left", "concrete_cover_min_right", "concrete_cover_min_bottom", "concrete_cover_different_at_section_sides_enabled", "concrete_durability", "concrete_durability_top", "concrete_durability_left", "concrete_durability_right", "concrete_durability_bottom", "concrete_shear_reinforcement_spans", "concrete_longitudinal_reinforcement_items", "member_concrete_design_uls_configuration", "member_concrete_design_sls_configuration", "member_concrete_design_fr_configuration", "member_concrete_design_seismic_configuration", "steel_effective_lengths", "steel_boundary_conditions", "steel_member_local_section_reduction", "steel_member_transverse_weld", "member_steel_design_uls_configuration", "member_steel_design_sls_configuration", "member_steel_design_fr_configuration", "timber_effective_lengths", "timber_service_class", "timber_moisture_class", "timber_service_conditions", "timber_member_local_section_reduction", "member_timber_design_uls_configuration", "member_timber_design_sls_configuration", "member_timber_design_fr_configuration", "end_modifications_member_start_extension", "end_modifications_member_start_slope_y", "end_modifications_member_start_slope_z", "end_modifications_member_end_extension", "end_modifications_member_end_slope_y", "end_modifications_member_end_slope_z", "has_any_end_modifications", "deflection_check_direction", "deflection_check_displacement_reference", "deflection_segments_z_axis", "deflection_segments_y_axis", "design_support_on_member_start", "design_support_on_member_end", "design_supports_on_internal_nodes", "deflection_segments_defined_length_z_axis_enabled", "deflection_segments_defined_length_y_axis_enabled", "member_type_spring", "member_type_damper_spring", "member_type_damper_damping_coefficient", "generating_object_info", "is_generated", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_DEACTIVATED_FOR_CALCULATION_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTRIBUTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    NODE_START_FIELD_NUMBER: _ClassVar[int]
    NODE_END_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_LENGTH_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_VOLUME_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_SURFACE_OF_COATING_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_MASS_FIELD_NUMBER: _ClassVar[int]
    SURFACE_OF_COATING_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    ANALYTICAL_CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_X_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_GRAVITY_Z_FIELD_NUMBER: _ClassVar[int]
    MEMBER_REPRESENTATIVE_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_VIA_MEMBER_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_VIA_PARENT_MEMBER_SET_FIELD_NUMBER: _ClassVar[int]
    DESIGN_PROPERTIES_PARENT_MEMBER_SET_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_RIB_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_FIRST_SURFACE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_SECOND_SURFACE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_SURFACE_ASSIGNMENT_AUTODETECT_FIELD_NUMBER: _ClassVar[int]
    ALIGN_LOCAL_Z_AXIS_TO_LOCAL_Z_AXIS_OF_SURFACE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_SHEAR_JOINT_BETWEEN_WEB_AND_FLANGE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_SURFACE_ROUGHNESS_CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_REDUCTION_OF_JOINT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    FLANGE_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    SYNCHRONIZE_WIDTH_MODE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_ORDINATES_MODE_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RIB_GENERATING_LONGITUDINAL_REINFORCEMENT_ITEMS_FROM_SURFACES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_DEFINABLE_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INTEGRATE_STRESSES_AND_FORCES_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_Y_Z_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_Y_PLUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_Z_PLUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_Y_MINUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_Z_MINUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_RADIUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_ALL_SURFACES_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_SURFACES_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_ALL_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_ALL_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_INCLUDE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_EXCLUDE_SURFACES_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_EXCLUDE_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    RESULT_BEAM_EXCLUDE_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    PROJECTED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_START_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_START_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_START_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_END_IS_DEFINED_AS_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_END_ABSOLUTE_FIELD_NUMBER: _ClassVar[int]
    SECTION_DISTANCE_FROM_END_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    SECTION_START_FIELD_NUMBER: _ClassVar[int]
    SECTION_END_FIELD_NUMBER: _ClassVar[int]
    SECTION_INTERNAL_FIELD_NUMBER: _ClassVar[int]
    SECTION_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    GRAIN_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    IS_CURVED_FIELD_NUMBER: _ClassVar[int]
    CURVED_MEMBER_IS_ASYMMETRIC_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    CURVED_MEMBER_IS_CANTILEVERS_FIELD_NUMBER: _ClassVar[int]
    CURVED_MEMBER_CANTILEVERS_TYPE_FIELD_NUMBER: _ClassVar[int]
    CURVED_MEMBER_IS_CAPPED_WITH_LOOSE_RIDGE_WEDGE_FIELD_NUMBER: _ClassVar[int]
    CURVED_MEMBER_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SPECIFICATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_ANGLE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_HELP_NODE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_PLANE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SURFACE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_SURFACE_PLANE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_ROTATED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_HINGE_START_FIELD_NUMBER: _ClassVar[int]
    MEMBER_HINGE_END_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ECCENTRICITY_START_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ECCENTRICITY_END_FIELD_NUMBER: _ClassVar[int]
    SUPPORT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TRANSVERSE_STIFFENER_FIELD_NUMBER: _ClassVar[int]
    MEMBER_OPENINGS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NONLINEARITY_FIELD_NUMBER: _ClassVar[int]
    MEMBER_RESULT_INTERMEDIATE_POINT_FIELD_NUMBER: _ClassVar[int]
    STRESS_ANALYSIS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_BOUNDARY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_MEMBER_LOCAL_SECTION_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    ALUMINUM_MEMBER_TRANSVERSE_WELD_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ALUMINUM_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ALUMINUM_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_USER_DEFINED_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_MIN_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_COVER_DIFFERENT_AT_SECTION_SIDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_TOP_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_LEFT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_RIGHT_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_DURABILITY_BOTTOM_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_SHEAR_REINFORCEMENT_SPANS_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_LONGITUDINAL_REINFORCEMENT_ITEMS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_CONCRETE_DESIGN_SEISMIC_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    STEEL_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    STEEL_BOUNDARY_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    STEEL_MEMBER_LOCAL_SECTION_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    STEEL_MEMBER_TRANSVERSE_WELD_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_STEEL_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    TIMBER_EFFECTIVE_LENGTHS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_SERVICE_CLASS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_MOISTURE_CLASS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_SERVICE_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    TIMBER_MEMBER_LOCAL_SECTION_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_ULS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_SLS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TIMBER_DESIGN_FR_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_START_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_START_SLOPE_Y_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_START_SLOPE_Z_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_END_EXTENSION_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_END_SLOPE_Y_FIELD_NUMBER: _ClassVar[int]
    END_MODIFICATIONS_MEMBER_END_SLOPE_Z_FIELD_NUMBER: _ClassVar[int]
    HAS_ANY_END_MODIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_CHECK_DISPLACEMENT_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_Z_AXIS_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_Y_AXIS_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORT_ON_MEMBER_START_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORT_ON_MEMBER_END_FIELD_NUMBER: _ClassVar[int]
    DESIGN_SUPPORTS_ON_INTERNAL_NODES_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_DEFINED_LENGTH_Z_AXIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEFLECTION_SEGMENTS_DEFINED_LENGTH_Y_AXIS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_SPRING_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_DAMPER_SPRING_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_DAMPER_DAMPING_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: MemberType
    is_deactivated_for_calculation: bool
    line: int
    section_distribution_type: MemberSectionDistributionType
    reference_type: MemberReferenceType
    nodes: _containers.RepeatedScalarFieldContainer[int]
    node_start: int
    node_end: int
    analytical_length: float
    analytical_volume: float
    analytical_surface_of_coating: float
    analytical_mass: float
    surface_of_coating: float
    analytical_center_of_gravity: _common_pb2.Vector3d
    analytical_center_of_gravity_x: float
    analytical_center_of_gravity_y: float
    analytical_center_of_gravity_z: float
    length: float
    volume: float
    mass: float
    center_of_gravity: _common_pb2.Vector3d
    center_of_gravity_x: float
    center_of_gravity_y: float
    center_of_gravity_z: float
    member_representative: int
    design_properties_via_member: bool
    design_properties_via_parent_member_set: bool
    design_properties_parent_member_set: int
    comment: str
    member_type_rib_alignment: MemberMemberTypeRibAlignment
    member_rib_first_surface: int
    member_rib_second_surface: int
    member_rib_surface_assignment_autodetect: bool
    align_local_z_axis_to_local_z_axis_of_surface: bool
    member_rib_shear_joint_between_web_and_flange: bool
    member_rib_surface_roughness_classification: MemberMemberRibSurfaceRoughnessClassification
    member_rib_reduction_of_joint_width: float
    flange_dimensions: ArrayOfMemberFlangeDimensions
    synchronize_width_mode: bool
    relative_ordinates_mode: bool
    member_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled: bool
    member_type_definable_stiffness: int
    result_beam_integrate_stresses_and_forces: MemberResultBeamIntegrateStressesAndForces
    result_beam_y_z: float
    result_beam_y_plus: float
    result_beam_z_plus: float
    result_beam_y_minus: float
    result_beam_z_minus: float
    result_beam_radius: float
    result_beam_include_all_surfaces: bool
    result_beam_include_surfaces: _containers.RepeatedScalarFieldContainer[int]
    result_beam_include_all_solids: bool
    result_beam_include_solids: _containers.RepeatedScalarFieldContainer[int]
    result_beam_include_all_members: bool
    result_beam_include_members: _containers.RepeatedScalarFieldContainer[int]
    result_beam_exclude_surfaces: _containers.RepeatedScalarFieldContainer[int]
    result_beam_exclude_solids: _containers.RepeatedScalarFieldContainer[int]
    result_beam_exclude_members: _containers.RepeatedScalarFieldContainer[int]
    projected_length: float
    section_distance_from_start_is_defined_as_relative: bool
    section_distance_from_start_absolute: float
    section_distance_from_start_relative: float
    section_distance_from_end_is_defined_as_relative: bool
    section_distance_from_end_absolute: float
    section_distance_from_end_relative: float
    section_alignment: MemberSectionAlignment
    section_start: int
    section_end: int
    section_internal: int
    section_material: int
    grain_alignment: MemberGrainAlignment
    is_curved: bool
    curved_member_is_asymmetric_layout: bool
    curved_member_is_cantilevers: bool
    curved_member_cantilevers_type: MemberCurvedMemberCantileversType
    curved_member_is_capped_with_loose_ridge_wedge: bool
    curved_member_parameters: ArrayOfMemberCurvedMemberParametersAndChildItems
    rotation_specification_type: MemberRotationSpecificationType
    rotation_angle: float
    rotation_help_node: int
    rotation_plane_type: MemberRotationPlaneType
    rotation_surface: int
    rotation_surface_plane_type: MemberRotationSurfacePlaneType
    is_rotated: bool
    member_hinge_start: int
    member_hinge_end: int
    member_eccentricity_start: int
    member_eccentricity_end: int
    support: int
    member_transverse_stiffener: int
    member_openings: int
    member_nonlinearity: int
    member_result_intermediate_point: int
    stress_analysis_configuration: int
    aluminum_effective_lengths: int
    aluminum_boundary_conditions: int
    aluminum_member_local_section_reduction: int
    aluminum_member_transverse_weld: int
    member_aluminum_design_uls_configuration: int
    member_aluminum_design_sls_configuration: int
    concrete_effective_lengths: int
    concrete_cover_user_defined_enabled: bool
    concrete_cover: float
    concrete_cover_top: float
    concrete_cover_left: float
    concrete_cover_right: float
    concrete_cover_bottom: float
    concrete_cover_min: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_top: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_left: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_right: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_min_bottom: _containers.RepeatedScalarFieldContainer[int]
    concrete_cover_different_at_section_sides_enabled: bool
    concrete_durability: int
    concrete_durability_top: int
    concrete_durability_left: int
    concrete_durability_right: int
    concrete_durability_bottom: int
    concrete_shear_reinforcement_spans: ArrayOfMemberConcreteShearReinforcementSpans
    concrete_longitudinal_reinforcement_items: ArrayOfMemberConcreteLongitudinalReinforcementItems
    member_concrete_design_uls_configuration: int
    member_concrete_design_sls_configuration: int
    member_concrete_design_fr_configuration: int
    member_concrete_design_seismic_configuration: int
    steel_effective_lengths: int
    steel_boundary_conditions: int
    steel_member_local_section_reduction: int
    steel_member_transverse_weld: int
    member_steel_design_uls_configuration: int
    member_steel_design_sls_configuration: int
    member_steel_design_fr_configuration: int
    timber_effective_lengths: int
    timber_service_class: int
    timber_moisture_class: int
    timber_service_conditions: int
    timber_member_local_section_reduction: int
    member_timber_design_uls_configuration: int
    member_timber_design_sls_configuration: int
    member_timber_design_fr_configuration: int
    end_modifications_member_start_extension: float
    end_modifications_member_start_slope_y: float
    end_modifications_member_start_slope_z: float
    end_modifications_member_end_extension: float
    end_modifications_member_end_slope_y: float
    end_modifications_member_end_slope_z: float
    has_any_end_modifications: bool
    deflection_check_direction: MemberDeflectionCheckDirection
    deflection_check_displacement_reference: MemberDeflectionCheckDisplacementReference
    deflection_segments_z_axis: ArrayOfMemberDeflectionSegmentsZAxis
    deflection_segments_y_axis: ArrayOfMemberDeflectionSegmentsYAxis
    design_support_on_member_start: int
    design_support_on_member_end: int
    design_supports_on_internal_nodes: ArrayOfMemberDesignSupportsOnInternalNodes
    deflection_segments_defined_length_z_axis_enabled: bool
    deflection_segments_defined_length_y_axis_enabled: bool
    member_type_spring: int
    member_type_damper_spring: int
    member_type_damper_damping_coefficient: float
    generating_object_info: str
    is_generated: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[MemberType, str]] = ..., is_deactivated_for_calculation: bool = ..., line: _Optional[int] = ..., section_distribution_type: _Optional[_Union[MemberSectionDistributionType, str]] = ..., reference_type: _Optional[_Union[MemberReferenceType, str]] = ..., nodes: _Optional[_Iterable[int]] = ..., node_start: _Optional[int] = ..., node_end: _Optional[int] = ..., analytical_length: _Optional[float] = ..., analytical_volume: _Optional[float] = ..., analytical_surface_of_coating: _Optional[float] = ..., analytical_mass: _Optional[float] = ..., surface_of_coating: _Optional[float] = ..., analytical_center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., analytical_center_of_gravity_x: _Optional[float] = ..., analytical_center_of_gravity_y: _Optional[float] = ..., analytical_center_of_gravity_z: _Optional[float] = ..., length: _Optional[float] = ..., volume: _Optional[float] = ..., mass: _Optional[float] = ..., center_of_gravity: _Optional[_Union[_common_pb2.Vector3d, _Mapping]] = ..., center_of_gravity_x: _Optional[float] = ..., center_of_gravity_y: _Optional[float] = ..., center_of_gravity_z: _Optional[float] = ..., member_representative: _Optional[int] = ..., design_properties_via_member: bool = ..., design_properties_via_parent_member_set: bool = ..., design_properties_parent_member_set: _Optional[int] = ..., comment: _Optional[str] = ..., member_type_rib_alignment: _Optional[_Union[MemberMemberTypeRibAlignment, str]] = ..., member_rib_first_surface: _Optional[int] = ..., member_rib_second_surface: _Optional[int] = ..., member_rib_surface_assignment_autodetect: bool = ..., align_local_z_axis_to_local_z_axis_of_surface: bool = ..., member_rib_shear_joint_between_web_and_flange: bool = ..., member_rib_surface_roughness_classification: _Optional[_Union[MemberMemberRibSurfaceRoughnessClassification, str]] = ..., member_rib_reduction_of_joint_width: _Optional[float] = ..., flange_dimensions: _Optional[_Union[ArrayOfMemberFlangeDimensions, _Mapping]] = ..., synchronize_width_mode: bool = ..., relative_ordinates_mode: bool = ..., member_rib_generating_longitudinal_reinforcement_items_from_surfaces_enabled: bool = ..., member_type_definable_stiffness: _Optional[int] = ..., result_beam_integrate_stresses_and_forces: _Optional[_Union[MemberResultBeamIntegrateStressesAndForces, str]] = ..., result_beam_y_z: _Optional[float] = ..., result_beam_y_plus: _Optional[float] = ..., result_beam_z_plus: _Optional[float] = ..., result_beam_y_minus: _Optional[float] = ..., result_beam_z_minus: _Optional[float] = ..., result_beam_radius: _Optional[float] = ..., result_beam_include_all_surfaces: bool = ..., result_beam_include_surfaces: _Optional[_Iterable[int]] = ..., result_beam_include_all_solids: bool = ..., result_beam_include_solids: _Optional[_Iterable[int]] = ..., result_beam_include_all_members: bool = ..., result_beam_include_members: _Optional[_Iterable[int]] = ..., result_beam_exclude_surfaces: _Optional[_Iterable[int]] = ..., result_beam_exclude_solids: _Optional[_Iterable[int]] = ..., result_beam_exclude_members: _Optional[_Iterable[int]] = ..., projected_length: _Optional[float] = ..., section_distance_from_start_is_defined_as_relative: bool = ..., section_distance_from_start_absolute: _Optional[float] = ..., section_distance_from_start_relative: _Optional[float] = ..., section_distance_from_end_is_defined_as_relative: bool = ..., section_distance_from_end_absolute: _Optional[float] = ..., section_distance_from_end_relative: _Optional[float] = ..., section_alignment: _Optional[_Union[MemberSectionAlignment, str]] = ..., section_start: _Optional[int] = ..., section_end: _Optional[int] = ..., section_internal: _Optional[int] = ..., section_material: _Optional[int] = ..., grain_alignment: _Optional[_Union[MemberGrainAlignment, str]] = ..., is_curved: bool = ..., curved_member_is_asymmetric_layout: bool = ..., curved_member_is_cantilevers: bool = ..., curved_member_cantilevers_type: _Optional[_Union[MemberCurvedMemberCantileversType, str]] = ..., curved_member_is_capped_with_loose_ridge_wedge: bool = ..., curved_member_parameters: _Optional[_Union[ArrayOfMemberCurvedMemberParametersAndChildItems, _Mapping]] = ..., rotation_specification_type: _Optional[_Union[MemberRotationSpecificationType, str]] = ..., rotation_angle: _Optional[float] = ..., rotation_help_node: _Optional[int] = ..., rotation_plane_type: _Optional[_Union[MemberRotationPlaneType, str]] = ..., rotation_surface: _Optional[int] = ..., rotation_surface_plane_type: _Optional[_Union[MemberRotationSurfacePlaneType, str]] = ..., is_rotated: bool = ..., member_hinge_start: _Optional[int] = ..., member_hinge_end: _Optional[int] = ..., member_eccentricity_start: _Optional[int] = ..., member_eccentricity_end: _Optional[int] = ..., support: _Optional[int] = ..., member_transverse_stiffener: _Optional[int] = ..., member_openings: _Optional[int] = ..., member_nonlinearity: _Optional[int] = ..., member_result_intermediate_point: _Optional[int] = ..., stress_analysis_configuration: _Optional[int] = ..., aluminum_effective_lengths: _Optional[int] = ..., aluminum_boundary_conditions: _Optional[int] = ..., aluminum_member_local_section_reduction: _Optional[int] = ..., aluminum_member_transverse_weld: _Optional[int] = ..., member_aluminum_design_uls_configuration: _Optional[int] = ..., member_aluminum_design_sls_configuration: _Optional[int] = ..., concrete_effective_lengths: _Optional[int] = ..., concrete_cover_user_defined_enabled: bool = ..., concrete_cover: _Optional[float] = ..., concrete_cover_top: _Optional[float] = ..., concrete_cover_left: _Optional[float] = ..., concrete_cover_right: _Optional[float] = ..., concrete_cover_bottom: _Optional[float] = ..., concrete_cover_min: _Optional[_Iterable[int]] = ..., concrete_cover_min_top: _Optional[_Iterable[int]] = ..., concrete_cover_min_left: _Optional[_Iterable[int]] = ..., concrete_cover_min_right: _Optional[_Iterable[int]] = ..., concrete_cover_min_bottom: _Optional[_Iterable[int]] = ..., concrete_cover_different_at_section_sides_enabled: bool = ..., concrete_durability: _Optional[int] = ..., concrete_durability_top: _Optional[int] = ..., concrete_durability_left: _Optional[int] = ..., concrete_durability_right: _Optional[int] = ..., concrete_durability_bottom: _Optional[int] = ..., concrete_shear_reinforcement_spans: _Optional[_Union[ArrayOfMemberConcreteShearReinforcementSpans, _Mapping]] = ..., concrete_longitudinal_reinforcement_items: _Optional[_Union[ArrayOfMemberConcreteLongitudinalReinforcementItems, _Mapping]] = ..., member_concrete_design_uls_configuration: _Optional[int] = ..., member_concrete_design_sls_configuration: _Optional[int] = ..., member_concrete_design_fr_configuration: _Optional[int] = ..., member_concrete_design_seismic_configuration: _Optional[int] = ..., steel_effective_lengths: _Optional[int] = ..., steel_boundary_conditions: _Optional[int] = ..., steel_member_local_section_reduction: _Optional[int] = ..., steel_member_transverse_weld: _Optional[int] = ..., member_steel_design_uls_configuration: _Optional[int] = ..., member_steel_design_sls_configuration: _Optional[int] = ..., member_steel_design_fr_configuration: _Optional[int] = ..., timber_effective_lengths: _Optional[int] = ..., timber_service_class: _Optional[int] = ..., timber_moisture_class: _Optional[int] = ..., timber_service_conditions: _Optional[int] = ..., timber_member_local_section_reduction: _Optional[int] = ..., member_timber_design_uls_configuration: _Optional[int] = ..., member_timber_design_sls_configuration: _Optional[int] = ..., member_timber_design_fr_configuration: _Optional[int] = ..., end_modifications_member_start_extension: _Optional[float] = ..., end_modifications_member_start_slope_y: _Optional[float] = ..., end_modifications_member_start_slope_z: _Optional[float] = ..., end_modifications_member_end_extension: _Optional[float] = ..., end_modifications_member_end_slope_y: _Optional[float] = ..., end_modifications_member_end_slope_z: _Optional[float] = ..., has_any_end_modifications: bool = ..., deflection_check_direction: _Optional[_Union[MemberDeflectionCheckDirection, str]] = ..., deflection_check_displacement_reference: _Optional[_Union[MemberDeflectionCheckDisplacementReference, str]] = ..., deflection_segments_z_axis: _Optional[_Union[ArrayOfMemberDeflectionSegmentsZAxis, _Mapping]] = ..., deflection_segments_y_axis: _Optional[_Union[ArrayOfMemberDeflectionSegmentsYAxis, _Mapping]] = ..., design_support_on_member_start: _Optional[int] = ..., design_support_on_member_end: _Optional[int] = ..., design_supports_on_internal_nodes: _Optional[_Union[ArrayOfMemberDesignSupportsOnInternalNodes, _Mapping]] = ..., deflection_segments_defined_length_z_axis_enabled: bool = ..., deflection_segments_defined_length_y_axis_enabled: bool = ..., member_type_spring: _Optional[int] = ..., member_type_damper_spring: _Optional[int] = ..., member_type_damper_damping_coefficient: _Optional[float] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfMemberFlangeDimensions(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberCurvedMemberParametersAndChildItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberConcreteShearReinforcementSpans(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberConcreteLongitudinalReinforcementItems(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberDeflectionSegmentsZAxis(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberDeflectionSegmentsYAxis(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArrayOfMemberDesignSupportsOnInternalNodes(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
