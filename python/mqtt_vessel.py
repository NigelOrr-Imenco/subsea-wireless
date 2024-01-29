#! /usr/bin/python
# Simulates a control system interfacing to a SWiG bridge over MQTT
# Based on simple example https://www.emqx.com/en/blog/how-to-use-mqtt-in-python#paho-mqtt-python-client-usage

from paho.mqtt import client as mqtt_client # Paho Python MQTT library
import logging
import random
import time

broker = "test.mosquitto.org" # Free broker for demonstration
# broker = "192.168.36.12" # Nigel's local broker
path = "swig/2024/example/protocol/bridge/" # Prefix for all messages
port = 1883
client_id = f'bridge-example-{random.randint(0, 1000)}'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)
        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)


def send(client, topic_suffix, message):
    # Send a message to a fully defined message topic based on provided suffix
    topic = f'{path}{topic_suffix}'
    result = client.publish(topic, message)
    if result[0] == 0:
        print(f"Sent `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send `{message}` to topic {topic}")


def request(client, device_id, endpoint):
    # Send a request for a SWiG endpoint
    topic = f'request/{device_id}'
    message = endpoint 
    send(client, topic, message)


# def load_swig_json():
#     # Load parameter definitions, map MQTT endpoints to protobuf IDs
#     with open('parameters.json') as json_file:
#     params = json.load(json_file)["all"]

# load_swig_json()
client = connect_mqtt()
client.on_disconnect = on_disconnect
for id in [2, 4]:
    request(client, id, "manufacturer_name")    # Poll requested endpoint
    request(client, id, "swig_version_major")    # Poll requested endpoint
    request(client, id, "swig_version_minor")    # Poll requested endpoint
    request(client, id, "background_noise")    # Poll requested endpoint
client.disconnect()