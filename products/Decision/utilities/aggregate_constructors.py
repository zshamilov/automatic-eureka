from products.Decision.framework.model import AggregateCreate, AggregateJson, AggregateUpdate


def aggregate_json_construct(aggregate_name, aggregate_variable_type,
                             aggregate_function, aggregate_description, grouping_element):
    return AggregateJson.construct(aggregateName=aggregate_name,
                                   aggregateVariableType=aggregate_variable_type,
                                   aggregateFunction=aggregate_function,
                                   aggregateDescription=aggregate_description,
                                   groupingElement=grouping_element)


def aggregate_construct(aggregate_name, aggregate_json,
                        aggregate_description=None, catalog_id=None):
    return AggregateCreate.construct(objectName=aggregate_name,
                                     aggregateDescription=aggregate_description,
                                     aggregateJson=aggregate_json,
                                     catalogId=catalog_id)


def aggregate_update_construct(aggregate_name, aggregate_json, aggregate_description=None):
    return AggregateUpdate.construct(objectName=aggregate_name,
                                     aggregateDescription=aggregate_description,
                                     aggregateJson=aggregate_json)
