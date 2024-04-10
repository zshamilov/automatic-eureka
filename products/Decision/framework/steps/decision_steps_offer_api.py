import base64

from products.Decision.framework.model import OfferCreateDto, OfferUpdateDto, OfferCreateUserVersionDto
from products.Decision.framework.scheme.decision_scheme_offer_api import DecisionOfferApi
from sdk.user import User


def get_offer_list(user: User, size=None):
    query = None
    offers = None
    if size is None:
        query = {
            "searchRequest": "eyJmaWx0ZXJzIjpbXSwic29ydHMiOltdLCJzZWFyY2hCeSI6IiIsInBhZ2UiOjEsInNpemUiOjEwMDAwMH0="}
        offers = user.with_api.send(DecisionOfferApi.get_offers(query))
    else:
        filt = f'{{"filters":[],"sorts":[],"searchBy":"","page":1,"size":{size}}}'
        list_query = base64.b64encode(bytes(filt, 'utf-8'))
        offers = user.with_api.send(DecisionOfferApi.get_offers(query={"searchRequest": list_query.decode(
            "utf-8")}))
    return offers


def offer_list_by_name(user: User, name: str):
    filt = f'{{"filters":[],"sorts":[{{"columnName":"changeDt","direction":"DESC"}}],"searchBy":"{name}","page":1,"size":999}}'
    list_query = base64.b64encode(bytes(filt, 'utf-8'))
    response = user.with_api.send(DecisionOfferApi.get_offers(query={"searchRequest": list_query.decode(
        "utf-8")}))
    if response.status == 204:
        return []
    else:
        offers = response.body["content"]
        return offers


def get_offer_info(user: User, version_id):
    return user.with_api.send(DecisionOfferApi.get_offer(version_id=version_id))


def get_offer_versions(user: User, offer_id):
    return user.with_api.send(DecisionOfferApi.get_offer_versions(offer_id=offer_id))


def create_offer(user: User, body: OfferCreateDto):
    return user.with_api.send(DecisionOfferApi.post_offer(body=body))


def create_offer_user_version(user: User, offer_id, body: OfferCreateUserVersionDto):
    return user.with_api.send(DecisionOfferApi.post_offer_user_version(offer_id=offer_id,
                                                                       body=body))


def delete_offer(user: User, version_id):
    return user.with_api.send(DecisionOfferApi.delete_offer(version_id=version_id))


def update_offer(user: User, version_id, body: OfferUpdateDto):
    return user.with_api.send(DecisionOfferApi.put_offer(version_id=version_id,
                                                         body=body))
