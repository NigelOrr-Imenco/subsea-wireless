# Create message, send over serial link to ROV wireless device 
from common import *
my_id = 1

device_status={2:{}, 3:{}}    # A blank place to store remote device status info as received

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORTS[DEVICES[my_id]]))
sock.setblocking(0)

request_stats = params.Message()
request_stats.source = my_id

for target in [2, 3]:   # Two SWiG wireless devices available, one wired, one remote
    request_stats.target = target
    # request_stats.requests[:] = [1, 2, 55]
    request_stats.requests[:] = [1, 2, 101, 55]
    # report(request_stats)

    sendMessage(request_stats, "rov")   # Vessel can only communicate through ROV modem
    waiting = True

    while waiting:
        try:
            data = None
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        except socket.error:    # Presume timeout
            pass        
        if data:    # Naively assume "any data is all data" for demo (e.g. not reassembling from fragments etc)
            # print(f"Received: {data}" % data)
            message = params.Message()
            message.ParseFromString(data)
            waiting = False # Successfully parsed
            if message.target == my_id:
                print(f"Message for me received from {message.source} ({DEVICES[message.source]}) - {len(data)} bytes")
                # print(str(message))
                for response in message.responses:
                    spec = get_specification(response.id)
                    # print(response, spec)
                    if spec["type"] == "uint8" or spec["type"] == "uint32":
                        device_status[message.source][response.id] = response.integer
                    elif spec["type"] == "string":
                        device_status[message.source][response.id] = response.string
                    elif spec["type"] == "boolean":
                        device_status[message.source][response.id] = response.bool
                    else:
                        print(f"No supported data type provided for parameter {response.id} in {str(response)}")
                        pass # Ignore it, nothing more can be done
                # print(device_status[message.source])  # Table for the device just received

            else: # Not for me, and I am an endpoint, so ignore it
                pass

#print(device_status)
print("|       *Manufacturer Name*       | *Ver.* | *Noise* |")
for device in [2, 3]:
    status = device_status[device]
    print(f'| {status[1]:<32}|  V{status[2]}.{status[101]}  |  {status[55]:^5}  |')
