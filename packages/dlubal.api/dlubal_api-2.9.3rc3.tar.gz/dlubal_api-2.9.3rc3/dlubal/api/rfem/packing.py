from dlubal.api.rfem.application_pb2 import Object, ObjectList
from google.protobuf.any_pb2 import Any
from google.protobuf.struct_pb2 import Value


def pack_object(object, model_id=None) -> Object:
    packed = Any()
    packed.Pack(object)

    if model_id is None:
        return Object(object=packed)

    return Object(object=packed, model_id=model_id)


def unpack_object(packed_object: Object, Type):
    result = Type()
    packed_object.object.Unpack(result)
    return result


def pack_object_list(object_list, model_id=None) -> ObjectList:
    packed_list = ObjectList()

    for object in object_list:
        packed_list.objects.append(pack_object(object, model_id))

    return packed_list


def unpack_object_list(packed_object_list: ObjectList, Type):
    unpacked_list = []

    for object in packed_object_list.objects:
        unpacked_list.append(unpack_object(object, Type))

    return unpacked_list


def get_internal_value(value: Value):
    '''
    Get the internal value stored in a generic Value object
    '''
    return getattr(value, value.WhichOneof('kind'))
