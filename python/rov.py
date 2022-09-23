# Modem on ROV attached to vessel
# Wait for serial/ethernet buffer to appear with message
# Act on it or pass it on
from common import *
my_id = 2

# Status of the various SWiG parameters with some initial demo values
my_status = {1:"Truly Fast Subsea Wireless Pty.", 2:1, 101:2, 55:63}

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORTS[DEVICES[my_id]]))
sock.setblocking(0)

while True:
    try:
        data = None
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    except socket.error:    # Presume timeout
        pass        
    if data:
        # print(f"Received: {data}" % data)
        message = params.Message()
        message.ParseFromString(data)
        if message.target == my_id:
            print(f"Message for me: device {message.target} ({DEVICES[message.target]})")
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
            print(f"Received data to relay - {len(data)} bytes for {DEVICES[message.target]}")
            sendMessage(message, DEVICES[message.target])







