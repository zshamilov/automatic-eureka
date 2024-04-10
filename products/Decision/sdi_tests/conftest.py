import base64
import json

import pytest

from common.generators import generate_string
from products.Decision.framework.model import ResponseDto, KafkaGetFullViewDto, KafkaCreateDto, \
    KafkaSettingsWithoutIdDto, KafkaAdditionalSettingsWithoutIdDto
from products.Decision.framework.steps.decision_steps_environments import env_id_by_name
from products.Decision.framework.steps.decision_steps_kafka import get_kafka_list, delete_kafka, get_kafka_info, \
    create_kafka
from products.Decision.framework.steps.decision_steps_schema import get_schema_list, delete_schema
from sdk.Admin.steps.admin_steps import search_user


@pytest.fixture()
def working_kafka(super_user):
    env_id = env_id_by_name(super_user, env_name="default_dev")
    kafka_param1 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="security.protocol",
                                                                 propertyValue="SASL_PLAINTEXT",
                                                                 propertySecure=False)
    kafka_param2 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.mechanism",
                                                                 propertyValue="SCRAM-SHA-512",
                                                                 propertySecure=False)
    kafka_param3 = KafkaAdditionalSettingsWithoutIdDto.construct(propertyName="sasl.jaas.config",
                                                                 propertyValue="org.apache.kafka.common"
                                                                               ".security.scram"
                                                                               ".ScramLoginModule required "
                                                                               "username=\"qa-dev-user\" "
                                                                               "password=\"fiUXC6rS2Iu953ecF1k3\";",
                                                                 propertySecure=False)
    kafka_settings = KafkaSettingsWithoutIdDto.construct(
        bootstrapServers="datasapience-kafka-bootstrap.kafka:9092",
        environmentId=env_id,
        kafkaAdditionalSettings=[kafka_param2,
                                 kafka_param1,
                                 kafka_param3])
    kafka_name = "qa_test_kafka_" + generate_string()
    broker_body = KafkaCreateDto.construct(name=kafka_name,
                                           description=None,
                                           kafkaSettings=[kafka_settings])
    kafka_create_result = ResponseDto.construct(**create_kafka(super_user, broker_body).body)
    kafka_info: KafkaGetFullViewDto = get_kafka_info(super_user, kafka_create_result.uuid)

    return kafka_info


@pytest.fixture(scope="class", autouse=True)
def objects_clean_up_sdi(request, admin, email, super_user) -> None:
    def clean_up_by_user_sdi():
        user_id = json.dumps([search_user(admin, email)[0]["id"]])
        filt = ('{"filters":[{"columnName":"lastChangeByUser","operator":"IN",'
                f'"values":{user_id}}}],"sorts":[{{"direction":'
                '"DESC","columnName":"changeDt"}],"page":1,"size":999}')
        list_query = {"searchRequest": base64.b64encode(bytes(filt, 'utf-8')).decode(
            "utf-8")}
        kafkas = get_kafka_list(super_user, list_query)
        schemas = get_schema_list(super_user).body

        for kafka in kafkas:
            vers_id = kafka["id"]
            try:
                delete_kafka(super_user, vers_id)
            except:
                print(f"can't delete broker: {vers_id}")
        for schema in schemas:
            if schema["name"].startswith("ag_scheme"):
                vers_id = schema["id"]
                try:
                    delete_schema(super_user, vers_id)
                except:
                    print(f"can't delete schemar: {vers_id}")

    request.addfinalizer(clean_up_by_user_sdi)