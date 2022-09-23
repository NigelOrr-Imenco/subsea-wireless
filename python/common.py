# Common functionality

import socket
import time
import parameters_pb2 as params
import json # To handle parameter file directly

UDP_IP = "127.0.0.1"
UDP_VESSEL_PORT = 55501
UDP_ROV_PORT = 55502
UDP_REMOTE_PORT = 55503
UDP_PORTS = {"vessel":UDP_VESSEL_PORT, "rov":UDP_ROV_PORT, "remote":UDP_REMOTE_PORT}
DEVICES = ["ZERO", "vessel", "rov", "remote"]
WIRELESS_LATENCY = 0.1  # Simulated latency in seconds

with open('parameters.json') as json_file:  # Provide wireless_parameter_specification dictionary for devices
    full_spec = json.load(json_file)["all"]
    # load the parameters into dictionary keyed by ID
    spec_by_id = {}
    for param in full_spec:
        spec_by_id[param["id"]] = param

def get_specification(id):
    return spec_by_id[id]


def report(proto, description=""):
    """ Display debug information about the message"""
    tx_bytes = proto.SerializeToString()
    print(f"{description} {str(tx_bytes)} ({len(tx_bytes)} bytes)")


def sendMessage(proto, portname):
    """ Send the message using UDP to a specified port"""
    buffer = proto.SerializeToString()
    time.sleep(WIRELESS_LATENCY)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(buffer, (UDP_IP, UDP_PORTS[portname]))
    print(f"Sent message to {portname} ({UDP_PORTS[portname]}) - {len(buffer)} bytes")
