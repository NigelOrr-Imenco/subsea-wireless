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
    print("serial to be added")
else:
    print(f"Interface definition not supported for {dry_interface_name} - {INTERFACES[dry_interface_name]}")

if INTERFACES[wet_interface_name][0] == "udp":
    wet_udp_in = getUdpInput("rov_wet")
elif INTERFACES[wet_interface_name][0] == "serial":
    print("serial to be added")
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
            print("Serial not supported yet")
    if not data:
        if INTERFACES[wet_interface_name][0] == "udp":
            try:
                data, addr = wet_udp_in.recvfrom(1024) # buffer size is 1024 bytes
            except socket.error:    # Presume timeout
                pass        
        elif INTERFACES[wet_interface_name][0] == "serial":
            print("Serial not supported yet")

    if data:
        # print(f"Received: {data}" % data)
        message = params.Message()
        message.ParseFromString(data)
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
            sendMessage(response, "vessel")
        else: # Not for me, pass to target
            print(f"Message to relay to device {message.target} ({PORTS[message.target]})")
            sendMessage(message, PORTS[message.target])