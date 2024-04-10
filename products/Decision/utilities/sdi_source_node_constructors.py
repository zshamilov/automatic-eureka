from products.Decision.framework.model import KafkaSourceNode, KafkaSourceKafkaNodeCfg, KafkaConsumerOffsets, \
    KafkaSinkNode, KafkaSinkKafkaNodeCfg, KafkaSinkProducerCfg, KafkaSourceConsumerCfg


def kafka_source_construct(kafka_id, schema_url: str, topic: str, start_offsets_type=None, stop_offsets_type=None,
                           parallelism=None, boundedness=None, group_id=None, message_format=None):
    start_offsets = KafkaConsumerOffsets.construct(type=start_offsets_type,
                                                   timestamp=None,
                                                   committed={})
    stop_offsets = KafkaConsumerOffsets.construct(type=stop_offsets_type,
                                                  timestamp=None,
                                                  committed={})
    kafka = KafkaSourceKafkaNodeCfg(
        consumer=KafkaSourceConsumerCfg(topic=topic, group_id=group_id, start_offsets=start_offsets,
                                        stop_offsets=stop_offsets,
                                        properties=[]))
    prop = KafkaSourceNode.construct(parallelism=parallelism,
                                     schema=schema_url,
                                     boundedness=boundedness,
                                     kafka_connection_uuid=kafka_id,
                                     serde={"json": {}, "csv": {}},
                                     kafka=kafka,
                                     security=None)
    return prop


def kafka_target_construct(kafka_id, topic: str, semantic=None,
                           parallelism=None, boundedness=None, message_format=None):
    producer = KafkaSinkProducerCfg.construct(topic=topic, semantic=semantic, properties=[])
    kafka = KafkaSinkKafkaNodeCfg.construct(bootstrap_servers=None,
                                            producer=producer)
    prop = KafkaSinkNode.construct(parallelism=parallelism,
                                   boundedness=boundedness,
                                   kafka_connection_uuid=kafka_id,
                                   serde={},
                                   kafka=kafka,
                                   security=None)
    return prop
