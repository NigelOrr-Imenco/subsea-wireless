# Modem on remote device
# Wait for simulated wet interface message
# Respond as appropriate
from common import *
my_id = 3

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORTS[DEVICES[my_id]]))
sock.setblocking(0)

# Status of the various SWiG parameters with some initial demo values
my_status = {1:"The Subsea Wireless Co. Ltd.", 2:1, 101:4, 55:35}

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
        # print(str(message))
        if message.target == my_id:
            print(f"Message for me: device {message.target} ({DEVICES[message.target]})")
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
            sendMessage(response, "rov")

        else: # Not for me, and I'm an endpoint, do nothing
            pass
