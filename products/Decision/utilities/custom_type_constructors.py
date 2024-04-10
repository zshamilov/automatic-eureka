import random
import string

from products.Decision.framework.model import AttributeCreate, ComplexTypeCreate, ComplexTypeUpdate, AttributeUpdate


def generate_attr_type_name(randomize: bool, const: bool, custom_type: bool, const_val: str):
    letters = string.ascii_lowercase
    rand_string_attr_name = ''.join(random.choice(letters) for i in range(16))
    new_attr_name = "attribute" + "_" + rand_string_attr_name
    new_type_name = "test_type" + "_" + rand_string_attr_name
    if randomize and not custom_type:
        return new_attr_name
    if randomize and custom_type:
        return new_type_name
    if const:
        return const_val


def attribute_construct(array_flag: bool = False, complex_flag: bool = False,
                        attr_name: str = "int_primitive_attribute",
                        complex_type_version_id=None, primitive_type_id: str = "1"):
    attribute = AttributeCreate.construct(attributeName=attr_name,
                                          complexFlag=complex_flag,
                                          arrayFlag=array_flag,
                                          primitiveTypeId=primitive_type_id,
                                          complexTypeVersionId=complex_type_version_id,
                                          description=None)

    return attribute


def type_create_construct(type_name, attrs):
    return ComplexTypeCreate.construct(objectName=type_name,
                                       displayName=type_name,
                                       description=None,
                                       attributes=attrs)


def create_attribute_construct(parent_id, array_flag: bool = False, complex_flag: bool = False,
                               attr_name: str = "attribute_made_in_test",
                               complex_type_version_id=None, primitive_type_id: str = "1"):
    attribute = AttributeCreate.construct(attributeName=attr_name,
                                          complexFlag=complex_flag,
                                          arrayFlag=array_flag,
                                          primitiveTypeId=primitive_type_id,
                                          complexTypeVersionId=complex_type_version_id,
                                          description=None, parentId=parent_id)

    return attribute


def type_update_construct(type_name, attrs, version_id, catalog_id=None):
    construct = ComplexTypeUpdate.construct(objectName=type_name,
                                            displayName=type_name,
                                            description=None,
                                            versionId=version_id,
                                            catalogId=catalog_id)
    if attrs is not None:
        construct.attributes = attrs
    return construct


def update_attribute_construct(parent_id, array_flag: bool = False, complex_flag: bool = False,
                               attr_name: str = "attribute_made_in_test",
                               complex_type_version_id=None, primitive_type_id: str = "1",
                               attribute_id=None):
    attribute = AttributeUpdate.construct(attributeName=attr_name,
                                          complexFlag=complex_flag,
                                          arrayFlag=array_flag,
                                          primitiveTypeId=primitive_type_id,
                                          complexTypeVersionId=complex_type_version_id,
                                          description=None, attributeId=attribute_id, parentId=parent_id)

    return attribute
