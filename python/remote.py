# Modem on remote device
# Wait for simulated wet interface message
# Respond as appropriate
from common import *
my_id = 4
my_name = PORTS[my_id]

if INTERFACES[my_name][0] == "udp":
    udp_in = getUdpInput(PORTS[my_id])
elif INTERFACES[my_name][0] == "serial":
    print("serial to be added")
else:
    print(f"Interface definition not supported for {my_name} - {INTERFACES[my_name]}")

# Status of the various SWiG parameters with some initial demo values
my_status = {1:"The Subsea Wireless Co. Ltd.", 2:1, 129:4, 55:35}

while True:
    data = None
    if INTERFACES[my_name][0] == "udp":
        try:
            data, addr = udp_in.recvfrom(1024) # buffer size is 1024 bytes
        except socket.error:    # Presume timeout
            pass        
    elif INTERFACES[my_name][0] == "serial":
        print("Serial not supported yet")
    if data:
        # print(f"Received: {data}" % data)
        message = params.Message()
        message.ParseFromString(cobs.decode(data))
        # print(str(message))
        if message.target == my_id:
            print(f"Message for me: device {message.target} ({PORTS[message.target]})")
            # Prepare response
            response = params.Message()
            response.source = my_id
            response.target = message.source
            # Handle sets
            # print(message.parameters)
            # Handle gets and populate responses
            for request in message.requests:
                try:
                    if type(my_status[request]) is int:
                        parameter=response.responses.add()
                        parameter.id = request
                        parameter.integer = my_status[request]
                    elif type(my_status[request]) is bool:
                        parameter=response.responses.add()
                        parameter.id = request
                        parameter.bool = my_status[request]
                    elif type(my_status[request]) is str:
                        parameter=response.responses.add()
                        parameter.id = request
                        parameter.string = my_status[request]
                except KeyError:    # No supported data, just leave it out
                    print(f"No data for requested parameter {request}")
                    pass
            # print(str(response))
            sendMessage(response, "rov_wet")    # Wireless interface

        else: # Not for me, and I'm an endpoint, do nothing
            pass
