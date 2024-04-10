from products.Decision.framework.model import KafkaGetFullViewDto, ResponseDto
from products.Decision.framework.scheme.decision_scheme_kafka import DecisionKafka
from sdk.user import User
from sdk.user.interface.api.response import ApiResponse


def create_kafka(user: User, body) -> ApiResponse:
    return user.with_api.send(DecisionKafka.post_kafka(body))


def get_kafka_info(user: User, kafka_id) -> KafkaGetFullViewDto:
    return KafkaGetFullViewDto.construct(**user.with_api.send(DecisionKafka.get_kafka(kafka_id)).body)


def delete_kafka(user: User, kafka_id) -> ResponseDto:
    return ResponseDto.construct(**user.with_api.send(DecisionKafka.delete_kafka(kafka_id=kafka_id)).body)


def get_kafka_list(user: User, query):
    return user.with_api.send(DecisionKafka.get_kafkas(query=query)).body.get("content") or []
