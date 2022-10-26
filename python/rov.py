# Modem on ROV attached to vessel
# Wait for serial/ethernet buffer to appear with message
# Act on it or pass it on
from common import *
my_id = 2
dry_interface_name = "rov_dry"
wet_interface_name = "rov_wet"

if INTERFACES[dry_interface_name][0] == "udp":
    dry_udp_in = getUdpInput("rov_dry")
elif INTERFACES[dry_interface_name][0] == "serial":
    import serial
    dry_serial = serial.Serial(INTERFACES[dry_interface_name][1], INTERFACES[dry_interface_name][2], timeout=0.1)
else:
    print(f"Interface definition not supported for {dry_interface_name} - {INTERFACES[dry_interface_name]}")

if INTERFACES[wet_interface_name][0] == "udp":
    wet_udp_in = getUdpInput("rov_wet")
elif INTERFACES[wet_interface_name][0] == "serial":
    import serial
    wet_serial = serial.Serial(INTERFACES[wet_interface_name][1], INTERFACES[wet_interface_name][2], timeout=0.1)
else:
    print(f"Interface definition not supported for {wet_interface_name} - {INTERFACES[wet_interface_name]}")

# Status of the various SWiG parameters with some initial demo values
my_status = {1:"Truly Fast Subsea Wireless Pty.", 2:1, 101:2, 55:63}

while True:
    data = None
    if not data:    # Service dry interface (note this line is superfluous but keeps processing of wet and dry the same)
        if INTERFACES[dry_interface_name][0] == "udp":
            try:
                data, addr = dry_udp_in.recvfrom(1024) # buffer size is 1024 bytes
            except socket.error:    # Presume timeout
                pass        
        elif INTERFACES[dry_interface_name][0] == "serial":
            data = dry_serial.read(1000)
    if not data:
        if INTERFACES[wet_interface_name][0] == "udp":
            try:
                data, addr = wet_udp_in.recvfrom(1024) # buffer size is 1024 bytes
            except socket.error:    # Presume timeout
                pass        
        elif INTERFACES[wet_interface_name][0] == "serial":
            data = wet_serial.read(1000)

    if data:
        # print(f"Received: {data}" % data)
        message = params.Message()
        message.ParseFromString(cobs.decode(data))
        if message.target == my_id:
            print(f"Message for me: device {message.target} ({PORTS[message.target]})")
            # Prepare response
            response = params.Message()
            response.source = my_id
            response.target = message.source
            # Handle sets
            # print(message.parameters)
            # Handle gets and populate responses
            for id in message.requests:
                parameter=response.responses.add()
                parameter.id = id
                spec = get_specification(id)  # Get the dictionary specification for this ID
                value = my_status.get(id, None)
                if spec["type"] == "uint8" or spec["type"] == "uint32":
                    parameter.integer = value
                elif spec["type"] == "string":
                    parameter.string = value
                elif spec["type"] == "boolean":
                    parameter.bool = value
                else:
                    print(f'unsupported data type for ID{parameter.id} - {spec["type"]}')
                    pass # Ignore it, nothing more can be done
            # print(str(response))
            # Vessel can only communicate through ROV modem's dry interface
            if INTERFACES[dry_interface_name][0] == "serial":
                sendMessage(response, "vessel", dry_serial)
            else:
                sendMessage(response, "vessel")   
        else: # Not for me, pass to target
            print(f"Message to relay to device {message.target} ({PORTS[message.target]})")
            if INTERFACES[PORTS[message.target]][0] == "serial":
                if message.target == 1: # Dry side
                    # print("Serial dry")
                    sendMessage(message, PORTS[message.target], dry_serial)
                else:
                    # print("Serial wet")
                    sendMessage(message, PORTS[message.target], wet_serial)
            else:
                # print("UDP")
                sendMessage(message, PORTS[message.target])