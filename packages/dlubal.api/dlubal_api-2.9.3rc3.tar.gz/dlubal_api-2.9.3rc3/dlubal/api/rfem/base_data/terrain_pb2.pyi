from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TerrainType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TERRAIN_TYPE_UNKNOWN: _ClassVar[TerrainType]
    TERRAIN_TYPE_BOREHOLES: _ClassVar[TerrainType]
    TERRAIN_TYPE_HORIZONTAL_PLANE: _ClassVar[TerrainType]
    TERRAIN_TYPE_INCLINED_PLANE: _ClassVar[TerrainType]
    TERRAIN_TYPE_NO_TERRAIN: _ClassVar[TerrainType]
    TERRAIN_TYPE_TABLE: _ClassVar[TerrainType]
TERRAIN_TYPE_UNKNOWN: TerrainType
TERRAIN_TYPE_BOREHOLES: TerrainType
TERRAIN_TYPE_HORIZONTAL_PLANE: TerrainType
TERRAIN_TYPE_INCLINED_PLANE: TerrainType
TERRAIN_TYPE_NO_TERRAIN: TerrainType
TERRAIN_TYPE_TABLE: TerrainType

class Terrain(_message.Message):
    __slots__ = ("no", "type", "comment", "bounding_box_offset_x", "bounding_box_offset_y", "center_of_terrain_z", "rotation_around_Z", "consider_boreholes", "coordinate_system", "terrain_table", "id_for_export_import", "metadata_for_export_import")
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_OFFSET_X_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_TERRAIN_Z_FIELD_NUMBER: _ClassVar[int]
    ROTATION_AROUND_Z_FIELD_NUMBER: _ClassVar[int]
    CONSIDER_BOREHOLES_FIELD_NUMBER: _ClassVar[int]
    COORDINATE_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TERRAIN_TABLE_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    type: TerrainType
    comment: str
    bounding_box_offset_x: float
    bounding_box_offset_y: float
    center_of_terrain_z: float
    rotation_around_Z: float
    consider_boreholes: bool
    coordinate_system: int
    terrain_table: ArrayOfTerrainTerrainTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., type: _Optional[_Union[TerrainType, str]] = ..., comment: _Optional[str] = ..., bounding_box_offset_x: _Optional[float] = ..., bounding_box_offset_y: _Optional[float] = ..., center_of_terrain_z: _Optional[float] = ..., rotation_around_Z: _Optional[float] = ..., consider_boreholes: bool = ..., coordinate_system: _Optional[int] = ..., terrain_table: _Optional[_Union[ArrayOfTerrainTerrainTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

class ArrayOfTerrainTerrainTable(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
