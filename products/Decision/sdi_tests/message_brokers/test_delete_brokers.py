import allure
import pytest
from requests import HTTPError

from common.generators import generate_string
from products.Decision.framework.model import KafkaAdditionalSettingsWithoutIdDto, KafkaSettingsWithoutIdDto, \
    KafkaCreateDto, ResponseDto, KafkaGetFullViewDto
from products.Decision.framework.steps.decision_steps_environments import env_id_by_name
from products.Decision.framework.steps.decision_steps_kafka import create_kafka, get_kafka_info, delete_kafka


@allure.epic("Брокеры сообщений")
@allure.feature("Удаление брокеров сообщений")
@pytest.mark.scenario("")
class TestCreateBroker:

    @allure.story("Удалённый брокер не находится в системе после удаления")
    @allure.title("Брокеры возможно удалить")
    def test_delete_kafka(self, super_user):
        with allure.step("Получить параметры окружения"):
            env_id = env_id_by_name(super_user, env_name="default_dev")
        with allure.step("Создание брокера с параметрами: sasl.jaas.config, sasl.mechanism, security.protocol"):
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
                                                                                       "password"
                                                                                       "=\"fiUXC6rS2Iu953ecF1k3\";",
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
        with allure.step("Получение информации о созданном брокере"):
            kafka_info: KafkaGetFullViewDto = get_kafka_info(super_user, kafka_create_result.uuid)
        with allure.step("Удаление созданного брокера"):
            delete_kafka(super_user, kafka_id=kafka_info.id)
        with allure.step("Удалённый брокер не найден"):
            with pytest.raises(HTTPError, match="404"):
                assert get_kafka_info(super_user, kafka_info.id)
