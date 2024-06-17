from confluent_kafka import Producer
import json
import ccloud_lib
import time
from datetime import datetime, timedelta
from data_fetcher import fetch_all_results


# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "velib-realtime-data"

# Create Producer instance
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer = Producer(producer_conf)

# Create topic if it doesn't already exist
ccloud_lib.create_topic(CONF, TOPIC)

delivered_records = 0

# Callback called acked (triggered by poll() or flush())
# when a message has been successfully delivered or
# permanently failed delivery (after retries).
def acked(err, msg):
    global delivered_records
    # Delivery report handler called on successful or failed delivery of message
    if err is not None:
        print("Failed to deliver message: {}".format(err))
    else:
        delivered_records += 1
        print("Produced record to topic {} partition [{}] @ offset {}"
                .format(msg.topic(), msg.partition(), msg.offset()))

try:
    end_time = datetime.now() + timedelta(days=4)
    while datetime.now() < end_time:
        # api_url1 = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records"
        api_url2 = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
    
        # all_results1 = fetch_all_results(api_url1, limit)
        all_results2 = fetch_all_results(api_url2,limit=100)

        # for result in all_results1:
        #     record_key = "velib_station"
        #     record_value = json.dumps(result)
        #     print("Producing record: {}\t{}".format(record_key, record_value))

        #     # This will actually send data to your topic
        #     producer.produce(
        #         TOPIC,
        #         key=record_key,
        #         value=record_value,
        #         on_delivery=acked
        #     )
        #     # p.poll() serves delivery reports (on_delivery)
        #     # from previous produce() calls thanks to acked callback
        #     producer.poll(0)

        for result in all_results2:
            record_key = "velib_status"
            record_value = json.dumps(result)
            print("Producing record: {}\t{}".format(record_key, record_value))

            # This will actually send data to your topic
            producer.produce(
                TOPIC,
                key=record_key,
                value=record_value,
                on_delivery=acked
            )
            # p.poll() serves delivery reports (on_delivery)
            # from previous produce() calls thanks to acked callback
            producer.poll(0)

        # if len(all_results1) < limit and len(all_results2) < limit:
        #     break

        time.sleep(3600)  # Attendre 1 h avant de récupérer les données suivantes
except KeyboardInterrupt:
    pass
finally:
    producer.flush()  # Finish producing the latest event before stopping the whole script
