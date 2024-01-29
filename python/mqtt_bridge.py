#! /usr/bin/python
# A simple MQTT to protobuf bridge

from paho.mqtt import client as mqtt_client # Paho Python MQTT library
import logging
import random
import time

from common import *    # Access common code
my_id = 1
my_name = PORTS[my_id]

if INTERFACES[my_name][0] == "udp":
    udp_in = getUdpInput(PORTS[my_id])
elif INTERFACES[my_name][0] == "serial":
    import serial
    dry_serial = serial.Serial(INTERFACES[PORTS[my_id]][1], INTERFACES[PORTS[my_id]][2], timeout=0.1)
else:
    print(f"Interface definition not supported for {my_name} - {INTERFACES[my_name]}")


broker = "test.mosquitto.org" # Free broker for demonstration
# broker = "192.168.36.12" # Nigel's local broker

path = "swig/2024/example/protocol/bridge/" # Prefix for all messages
port = 1883
client_id = f'bridge-example-{random.randint(0, 1000)}'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

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
    result = client.publish(f'{topic}', message)
    if result[0] == 0:
        print(f"Sent `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send `{message}` to topic {topic}")


def mqtt_request_handler(client, userdata, msg):
    """ Handle requests, create protobuf message and send it"""
    topic_path= msg.topic.split('/')    # Extract hierarchy of topic
    waiting = False # Set if waiting for response from device
    if topic_path[-2] == 'request':
        target = int(topic_path[-1])   # Last level of path is target ID
        endpoint = get_specification(msg.payload.decode())
        print(f"Forwarding request for `{endpoint["description"]}` towards ID {topic_path[-1]}")
        # Create request
        request_stats = params.Message()
        request_stats.source = my_id
        request_stats.target = target
        request_stats.requests[:] = [endpoint["id"]]
        # print(request_stats)
    # Vessel can only communicate through ROV modem's dry interface
        if INTERFACES[my_name][0] == "serial":
            sendMessage(request_stats, "rov_dry", dry_serial)
        else:
            sendMessage(request_stats, "rov_dry")   
        waiting = True
    else:
        print(f"Received unhandled topic `{msg.topic}`: `{msg.payload.decode()}`")

    while waiting:
        data = None
        if INTERFACES[my_name][0] == "udp":
            try:
                data, addr = udp_in.recvfrom(1024) # buffer size is 1024 bytes
            except socket.error:    # Presume timeout
                pass        
        elif INTERFACES[my_name][0] == "serial":
            data = dry_serial.read(1000)

        if data:    # Naively assume "any data is all data" for demo (e.g. not reassembling from fragments etc)
            # print(f"Received: {data}" % data)
            message = params.Message()
            message.ParseFromString(cobs.decode(data))
            waiting = False # Successfully parsed
            if message.target == my_id:
                print(f"Message for me received from {message.source} ({PORTS[message.source]}) - {len(data)} bytes")
                # print(str(message))
                for response in message.responses:
                    spec = get_specification(response.id)
                    # print(response, spec)
                    if spec["representation"] == "uint8" or spec["representation"] == "uint32":
                        payload = str(response.integer)
                    elif spec["representation"] == "string":
                        payload = response.string
                    elif spec["representation"] == "boolean":
                        payload = str(response.bool)
                    else:
                        print(f"No supported data type provided for parameter {response.id} in {str(response)}")
                        pass # Ignore it, nothing more can be done
                    topic_suffix = f"{message.source}/{spec["name"]}"
                    send(client, topic_suffix, payload)

            else: # Not for me, and I am an endpoint, so ignore it
                pass


client = connect_mqtt()
client.on_disconnect = on_disconnect
print(f"Subscribing to {path}request/#")
client.subscribe(f'{path}request/#')   # Catch polling from upstream
client.on_message = mqtt_request_handler
client.loop_forever()