from products.Decision.framework.model import OfferCreateDto, OfferUpdateDto, OfferCreateUserVersionDto
from sdk.user.interface.api.request import ApiRequest


class DecisionOfferApi:
    @staticmethod
    def get_offers(query) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/offer",
            query=query,
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def post_offer(body: OfferCreateDto) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/offer",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def post_offer_user_version(offer_id, body: OfferCreateUserVersionDto) -> ApiRequest:
        return ApiRequest(
            method="POST",
            path=f"/offer/{offer_id}/create/userVersion",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def delete_offer(version_id: str) -> ApiRequest:
        return ApiRequest(
            method="DELETE",
            path=f"/offer/{version_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_offer(version_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/offer/{version_id}",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def get_offer_versions(offer_id: str) -> ApiRequest:
        return ApiRequest(
            method="GET",
            path=f"/offer/{offer_id}/versions",
            query={},
            body={},
            headers={"Content-Type": "application/json"},
        )

    @staticmethod
    def put_offer(version_id: str, body: OfferUpdateDto) -> ApiRequest:
        return ApiRequest(
            method="PUT",
            path=f"/offer/{version_id}",
            query={},
            body=body.dict(),
            headers={"Content-Type": "application/json"},
        )