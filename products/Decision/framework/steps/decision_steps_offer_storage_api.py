from products.Decision.framework.scheme.decision_scheme_offer_storage_api import DecisionOfferStorageApi
from sdk.user import User


def get_offer_storage_client_id_types(user: User):
    return user.with_api.send(DecisionOfferStorageApi.get_client_id_types())