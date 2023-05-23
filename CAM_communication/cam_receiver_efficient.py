import json
import select
import socket

def receive_cam_udp(sock):

    print("UDP server listening on {}:{}".format(host, port))

    while True:
        # Yield at least all 0.2 seconds so CPU is not blocked all the time
        ready, _, _ = select.select([sock], [], [], 0.2)

        if ready:
            data, addr = sock.recvfrom(1024)
            json_data = data.decode('utf-8')
            payload = json.loads(json_data)
            print("Received payload:")
            print(payload)
            print("")
    sock.close()

# needs other IP if listening to broadcast
# Broadcast addr = 10.255.255.255 on Pi2
try:
    host = '10.255.255.255'
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    while True:
        receive_cam_udp(sock)
except KeyboardInterrupt:
    pass
finally:
    sock.close()