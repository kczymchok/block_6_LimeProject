from confluent_kafka import Producer
import json
import ccloud_lib
import time
from datetime import datetime, timedelta
from data_fetcher import fetch_all_results


CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "velib-realtime-data"


producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer = Producer(producer_conf)


ccloud_lib.create_topic(CONF, TOPIC)

delivered_records = 0

def acked(err, msg):
    global delivered_records

    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        delivered_records += 1
        print("Produced record to topic {} partition [{}] @ offset {}"
                .format(msg.topic(), msg.partition(), msg.offset()))

try:
    end_time = datetime.now() + timedelta(days=4)
    while datetime.now() < end_time:

        api_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
    
        all_results = fetch_all_results(api_url,limit=100)


        for result in all_results:
            record_key = "velib_status"
            record_value = json.dumps(result)
            print("Producing record: {}\t{}".format(record_key, record_value))

            producer.produce(
                TOPIC,
                key=record_key,
                value=record_value,
                on_delivery=acked
            )

            producer.poll(0)


        time.sleep(3600)
except KeyboardInterrupt:
    pass
finally:
    producer.flush()
