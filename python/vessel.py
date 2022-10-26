# Create message, send over serial link to ROV wireless device 
from common import *
my_id = 1
my_name = PORTS[my_id]

if INTERFACES[my_name][0] == "udp":
    udp_in = getUdpInput(PORTS[my_id])
elif INTERFACES[my_name][0] == "serial":
    import serial
    dry_serial = serial.Serial(INTERFACES[PORTS[my_id]][1], INTERFACES[PORTS[my_id]][2], timeout=0.1)
else:
    print(f"Interface definition not supported for {my_name} - {INTERFACES[my_name]}")

device_status={2:{}, 4:{}}    # A blank place to store remote device status info as received

request_stats = params.Message()
request_stats.source = my_id

for target in [2, 4]:   # Two SWiG wireless devices available, one wired, one remote
    request_stats.target = target
    # request_stats.requests[:] = [1, 2, 55]
    request_stats.requests[:] = [1, 2, 101, 55]
    # report(request_stats)

# Vessel can only communicate through ROV modem's dry interface
    if INTERFACES[my_name][0] == "serial":
        sendMessage(request_stats, "rov_dry", dry_serial)
    else:
        sendMessage(request_stats, "rov_dry")   
    waiting = True

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
            message.ParseFromString(data)
            waiting = False # Successfully parsed
            if message.target == my_id:
                print(f"Message for me received from {message.source} ({PORTS[message.source]}) - {len(data)} bytes")
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

# print(device_status)  # unformatted for debug
print("|       *Manufacturer Name*       | *Ver.* | *Noise* |")
for device in [2, 4]:
    status = device_status[device]
    print(f'| {status[1]:<32}|  V{status[2]}.{status[101]}  |  {status[55]:^5}  |')
