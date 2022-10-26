# Common functionality
from cobs import cobs
import json # To handle parameter file directly
import socket
import time
import parameters_pb2 as params

UDP_IP = "127.0.0.1"
UDP_VESSEL_PORT = 55501
UDP_ROV_DRY_PORT = 55502
UDP_ROV_WET_PORT = 55522
UDP_REMOTE_PORT = 55503
# UDP_PORTS = {"vessel":UDP_VESSEL_PORT, "rov":UDP_ROV_PORT, "remote":UDP_REMOTE_PORT}
INTERFACES = {
    # "vessel":["udp", UDP_IP, UDP_VESSEL_PORT],
    "vessel":["serial", "COM8", 19200],
    # "rov_dry":["udp", UDP_IP, UDP_ROV_DRY_PORT],
    "rov_dry":["serial", "COM9", 19200],
    "rov_wet":["udp", UDP_IP, UDP_ROV_WET_PORT],
    "remote":["udp", UDP_IP, UDP_REMOTE_PORT],
    }
PORTS = ["ZERO", "vessel", "rov_dry", "rov_wet", "remote"]
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


def sendMessage(proto, portname, port_handle=None):
    """ Send the message to a specified interface"""
    buffer = cobs.encode(proto.SerializeToString())
    time.sleep(WIRELESS_LATENCY)
    if INTERFACES[portname][0] == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(buffer, (INTERFACES[portname][1], INTERFACES[portname][2]))
        print(f"Sent UDP message to {portname} ({INTERFACES[portname][1]}:{INTERFACES[portname][2]}) - {len(buffer)} bytes")
    elif INTERFACES[portname][0] == "serial":
        port_handle.write(buffer)
        print(f"Sent serial message to {portname} ({INTERFACES[portname][1]}) - {len(buffer)} bytes")
    else:
        print(f"Interface definition not supported for {portname} - {INTERFACES[portname]}")


def getUdpInput(portname):
    print(f'Getting UDP for {portname}')
    sock = socket.socket(socket.AF_INET, # Internet
            socket.SOCK_DGRAM) # UDP
    sock.bind((INTERFACES[portname][1], INTERFACES[portname][2]))
    sock.setblocking(0)
    return sock