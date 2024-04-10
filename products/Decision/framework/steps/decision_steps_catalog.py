import base64

from products.Decision.framework.model import CatalogUpdate, CatalogMove, DiagramCatalogShortInfoView, \
    ComplexTypeCatalogShortView, ExternalServiceCatalogShortInfoDto, AggregateCatalogGetFullView, DiagramShortInfoView, \
    ObjectType
from products.Decision.framework.scheme.decision_scheme_catalog import DecisionCatalog
from products.Decision.framework.scheme.decision_scheme_communication_api import DecisionCommunication
from products.Decision.framework.scheme.decision_scheme_complex_type import DecisionComplexType
from products.Decision.framework.scheme.decision_scheme_custom_attr_dict import DecisionCustomAttrDictApi
from products.Decision.framework.scheme.decision_scheme_diagram import DecisionDiagram
from products.Decision.framework.scheme.decision_scheme_external_service_api import DecisionExternalServiceApi
from products.Decision.framework.scheme.decision_scheme_offer_api import DecisionOfferApi
from products.Decision.framework.scheme.decision_scheme_script_api import DecisionScripts
from sdk.user import User


def create_catalog(user: User, body):
    return user.with_api.send(DecisionCatalog.post_catalog(body=body))


def delete_catalogs(user: User, catalog_ids: [str]):
    query = {"ids": catalog_ids}
    return user.with_api.send(DecisionCatalog.delete_catalog(query=query))


def get_all_catalogs(user: User, query=None):
    if query is None:
        str_query = '{"filters":[],"sorts":[],"page":1,"size":999}'
        q_enc = base64.b64encode(bytes(str_query, "utf-8"))
        query = {"searchRequest": q_enc.decode("utf-8")}
    return user.with_api.send(DecisionCatalog.get_catalogs(query=query))


def get_catalog_by_name(user: User, catalog_name: str):
    str_query = f'{{"filters":[],"sorts":[],"searchBy":"{catalog_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_catalogs(query=query))


def update_catalog(user: User, updated_name: str, catalog_id):
    body = CatalogUpdate.construct(catalogId=catalog_id,
                                   catalogName=updated_name)
    return user.with_api.send(DecisionCatalog.put_catalog(body))


def move_element_in_catalog(user: User, target_catalog_id, element_id):
    body = CatalogMove.construct(catalogId=target_catalog_id,
                                 elementId=element_id)
    return user.with_api.send(DecisionCatalog.put_catalog_move(body))


def get_types_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_types_catalogs(query=query))


def find_type_in_types_catalogs(user: User, type_version_id, catalog_id=None, type_name=None) \
        -> ComplexTypeCatalogShortView:
    str_query = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if type_name is not None:
        str_query = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{type_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCatalog.get_types_catalogs(query=query))
    c_type = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["versionId"] == type_version_id:
                c_type = ComplexTypeCatalogShortView.construct(**el)
                break
    return c_type


def find_func_in_funcs_catalogs(user: User, func_id, catalog_id=None, func_name=None) \
        -> ComplexTypeCatalogShortView:
    str_query = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if func_name is not None:
        str_query = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{func_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCatalog.get_user_funcs_catalogs(query=query))
    c_type = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["id"] == func_id:
                c_type = ComplexTypeCatalogShortView.construct(**el)
                break
    return c_type


def find_service_in_services_catalogs(user: User, service_version_id, catalog_id=None, service_name=None) \
        -> ExternalServiceCatalogShortInfoDto:
    str_query = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if service_name is not None:
        str_query = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{service_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCatalog.get_services_catalogs(query=query))
    print("resp", resp)
    c_type = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["versionId"] == service_version_id:
                c_type = ExternalServiceCatalogShortInfoDto.construct(**el)
                break
    return c_type


def get_funcs_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_user_funcs_catalogs(query=query))


def find_aggregate_in_aggregates_catalogs(user: User, aggregate_version_id, catalog_id=None, aggregate_name=None) \
        -> AggregateCatalogGetFullView:
    str_query = '{"filters":[],"sorts":[],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if aggregate_name is not None:
        str_query = f'{{"filters":[],"sorts":[],"searchBy":"{aggregate_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCatalog.get_aggregate_catalogs(query=query))
    aggr = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["versionId"] == aggregate_version_id:
                aggr = AggregateCatalogGetFullView.construct(**el)
                break
    return aggr


def get_diagrams_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_diagrams_catalogs(query=query))


def get_scripts_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_scripts_catalogs(query=query))


def get_services_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_services_catalogs(query=query))


def get_aggregates_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_aggregate_catalogs(query=query))


def get_offers_catalog_content_by_id(user: User, catalog_id):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                f',"sorts":[],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    return user.with_api.send(DecisionCatalog.get_offer_catalogs(query=query))


def find_offer_in_offers_catalogs(user: User, offer_version_id, catalog_id=None, offer_name=None) \
        -> DiagramShortInfoView:
    str_query = '{"filters":[],"sorts":[{"columnName":"changeDt","direction":"DESC"}],"page":1,"size":20}'
    if catalog_id is not None:
        str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":"{catalog_id}"}}]' \
                    f',"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"page":1,"size":20,"currentCatalogId":"{catalog_id}"}}'
    if offer_name is not None:
        str_query = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{offer_name}","page":1,"size":20}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    print(query)
    resp = user.with_api.send(DecisionCatalog.get_offer_catalogs(query=query))
    print("resp", resp)
    offers = None
    if resp.status != 204:
        for el in resp.body["content"]:
            if el["versionId"] == offer_version_id:
                offers = DiagramShortInfoView.construct(**el)
                break
    return offers


def find_catalog_in_diagram_catalog_by_id(user: User, catalog_id, size=10):
    str_query = f'{{"filters":[],"sorts":[{{"direction":"DESC","columnName":"changeDt"}}],"page":1,"size":{size}}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    searched_el = None
    response = user.with_api.send(DecisionCatalog.get_diagrams_catalogs(query=query)).body["content"]
    for el in response:
        if el["catalogId"] == catalog_id:
            searched_el = DiagramCatalogShortInfoView.construct(**el)
            break
    return searched_el


def find_catalog_in_parent_catalog_by_id(user: User, parent_catalog_id, catalog_id, size=20):
    str_query = f'{{"filters":[{{"columnName":"catalogId","operator":"EQUAL","value":{parent_catalog_id}}}],' \
                f'"sorts":[{{"direction":"DESC","columnName":"changeDt"}}], ' \
                f'"page":1,"size":{size},"currentCatalogId":{parent_catalog_id}}}'
    q_enc = base64.b64encode(bytes(str_query, "utf-8"))
    query = {"searchRequest": q_enc.decode("utf-8")}
    searched_el = None
    response = user.with_api.send(DecisionCatalog.get_diagrams_catalogs(query=query)).body["content"]
    for el in response:
        if el["catalogId"] == catalog_id:
            searched_el = DiagramCatalogShortInfoView.construct(**el)
            break
    return searched_el


def get_objects_by_query(user: User, query):
    objects = dict()
    objects[ObjectType.DIAGRAM.value] = user.with_api.send(
        DecisionDiagram.get_diagrams(query)).body.get("content") or []
    objects[ObjectType.CUSTOM_CODE.value] = user.with_api.send(
        DecisionScripts.get_scripts(query)).body.get("content") or []
    objects[ObjectType.COMPLEX_TYPE.value] = user.with_api.send(
        DecisionComplexType.get_complex_types(query)).body.get("content") or []
    objects[ObjectType.COMMUNICATION_CHANNEL.value] = user.with_api.send(
        DecisionCommunication.get_communications(query)).body.get("content") or []
    objects[ObjectType.OFFER.value] = user.with_api.send(
        DecisionOfferApi.get_offers(query)).body.get("content") or []
    objects[ObjectType.CUSTOM_ATTRIBUTE_DICTIONARY.value] = user.with_api.send(
        DecisionCustomAttrDictApi.get_custom_attributes(query)).body.get("content") or []
    objects[ObjectType.SERVICE.value] = user.with_api.send(
        DecisionExternalServiceApi.get_services(query)).body.get("content") or []
    return objects
