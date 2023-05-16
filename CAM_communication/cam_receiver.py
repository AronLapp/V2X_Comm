import json
import socket


def receive_cam_udp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((host, port))

    print("UDP server listening on {}:{}".format(host, port))

    while True:
        data, addr = sock.recvfrom(1024)

        json_data = data.decode('utf-8')

        payload = json.loads(json_data)

        print("Received payload:")
        print(payload)
        print("")

    sock.close()


# needs other IP if listening to broadcast
receive_cam_udp('127.0.0.1', 5000)