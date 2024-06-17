# from confluent_kafka import Consumer, KafkaError
# import json
# import ccloud_lib
# import time
# import pandas as pd
# import boto3
# import os
# from datetime import datetime

# # Initialize configurations from "python.config" file
# CONF = ccloud_lib.read_ccloud_config("python.config")
# TOPIC = "velib-realtime-data"

# # AWS S3 configurations
# s3_bucket = "velib-project"
# aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key
# )


# # Create Consumer instance
# # 'auto.offset.reset=earliest' to start reading from the beginning of the
# # topic if no committed offsets exist
# consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
# consumer_conf['group.id'] = 'velib_consumer'
# consumer_conf['auto.offset.reset'] = 'earliest'
# consumer = Consumer(consumer_conf)

# # Subscribe to topic
# consumer.subscribe([TOPIC])

# # Process messages
# try:
#     while True:
#         msg = consumer.poll(timeout=-1)
#         if msg is None:
#             print("Waiting for message or event/error in poll()")
#             continue
#         elif msg.error():
#             print('Error: {}'.format(msg.error()))
#         else:
#             record_key = msg.key().decode("utf-8")
#             record_value = msg.value().decode("utf-8")
            
#             # Vérifier la clé et décoder la valeur JSON
#             # if record_key == "velib_station":
#             #     data = json.loads(record_value)
#             #     # Traiter les données de l'URL "velib-disponibilite-en-temps-reel"
#             #     # Créer un DataFrame, effectuer des opérations, etc.
#             #     current_date = datetime.now().strftime("%Y-%m-%d")
#             #     object_key = f"data_velib_station/{record_key}_{current_date}_{int(time.time())}.json"

#             #     try:

#             #         s3_client.put_object(
#             #             Bucket=s3_bucket,
#             #             Key=object_key,
#             #             Body=json.dumps(data)
#             #         )
#             #         print(f"Uploaded data to S3: {object_key}")
                
#             #     except Exception as e: 
#             #         print(f"Error uploading data to S3: {e}")

                
#             #     print(f"Uploaded data to S3: {object_key}")
#             #     print(data)


#             if record_key == "velib_status":
#                 data = json.loads(record_value)
#                 # Traiter les données de l'URL "velib-emplacement-des-stations"
#                 # Créer un DataFrame, effectuer des opérations, etc.
#                 current_date = datetime.now().strftime("%Y-%m-%d")
#                 object_key = f"realtime_data_velib/{record_key}_{current_date}_{int(time.time())}.json"

#                 try:

#                     s3_client.put_object(
#                         Bucket=s3_bucket,
#                         Key=object_key,
#                         Body=json.dumps(data)
#                     )
                
#                     print(f"Uploaded data to S3: {object_key}")

#                 except Exception as e:
#                     print(f"Error uploading data to S3: {e}")

#                 print(f"Uploaded data to S3 real time status: {object_key}")
#                 print(data)
              
        
#         time.sleep(2.0)  # Attendre une demi-seconde entre les messages
# except KeyboardInterrupt:
#     pass
# finally:
#     consumer.close()


from confluent_kafka import Consumer, KafkaError
import json
import ccloud_lib
import time
import boto3
import os
from datetime import datetime

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "velib-realtime-data"

# AWS S3 configurations
s3_bucket = "velib-project"
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Create Consumer instance
consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
consumer_conf['group.id'] = 'velib_consumer'
consumer_conf['auto.offset.reset'] = 'earliest'
consumer = Consumer(consumer_conf)

# Subscribe to topic
consumer.subscribe([TOPIC])

# Process messages
try:
    accumulated_data = []
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        elif msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print('%% %s [%d] reached end at offset %d\n' %
                      (msg.topic(), msg.partition(), msg.offset()))
            else:
                print('Error: {}'.format(msg.error()))
                continue

        else:
            record_key = msg.key().decode("utf-8")
            record_value = msg.value().decode("utf-8")
            
            if record_key == "velib_status":
                data = json.loads(record_value)
                accumulated_data.append(data)

                # Log each message
                print(f"Received message: {data}")

                # Optional: commit offset after each message
                consumer.commit()

        # Upload accumulated data in batches
        if len(accumulated_data) >= 100:  # Adjust the batch size as needed
            current_date = datetime.now().strftime("%Y-%m-%d")
            object_key = f"realtime_data_velib/{record_key}_{current_date}_{int(time.time())}.json"
            try:
                s3_client.put_object(
                    Bucket=s3_bucket,
                    Key=object_key,
                    Body=json.dumps(accumulated_data)
                )
                print(f"Uploaded batch data to S3: {object_key}")
                accumulated_data = []  # Reset after upload
            except Exception as e:
                print(f"Error uploading data to S3: {e}")

        time.sleep(2.0)  # Adjust the sleep interval as necessary

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
