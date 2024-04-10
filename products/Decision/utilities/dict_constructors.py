from products.Decision.framework.model import CustomAttributeDictionaryUpdate, CustomAttributeDictionaryValueCreate, \
    CustomAttributeDictionaryValueUpdate, CustomAttributeDictionaryCreate


def dict_value_construct(dict_value, dict_value_display_name, value_id=None, op="create"):
    if op == "create":
        return CustomAttributeDictionaryValueCreate.construct(dictValue=dict_value,
                                                              dictValueDisplayName=dict_value_display_name)
    if op == "update":
        return CustomAttributeDictionaryValueUpdate.construct(dictValue=dict_value,
                                                              dictValueDisplayName=dict_value_display_name,
                                                              id=value_id)


def dict_construct(dict_name, dict_value_type_id, values, op="create", dict_id=None):
    if op == "create":
        return CustomAttributeDictionaryCreate.construct(dictName=dict_name,
                                                         dictValueTypeId=dict_value_type_id,
                                                         values=values)
    if op == "update":
        return CustomAttributeDictionaryUpdate.construct(dictName=dict_name,
                                                         id=dict_id,
                                                         dictValueTypeId=dict_value_type_id,
                                                         values=values)
