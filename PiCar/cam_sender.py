import json
import socket
import time


def generate_payload(ticks, latitude, longitude, vel, direct):
    with open('../cam_msg.json') as file:
        template_payload = json.load(file)

        template_payload['position']['ticks'] = ticks
        template_payload['position']['latitude'] = latitude
        template_payload['position']['longitude'] = longitude
        template_payload['velocity'] = vel
        template_payload['direction'] = direct
    payload = template_payload
    return payload


def send_cam_udp(ticks, latitude, longitude, vel, direct):
    # requires actual values
    host = "127.0.0.1"
    port = 5000

    payload = generate_payload(ticks, latitude, longitude, vel, direct)
    # convert payload into json, json into bytes
    json_payload = json.dumps(payload).encode('utf-8')

    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send UDP packet
    sock.sendto(json_payload, (host, port))
    print("Sent payload " + str(payload))

    sock.close()


def send_cam_broadcast(ticks, latitude, longitude, vel, direct):
    # requires actual values
    broadcast_address = '10.255.255.255'
    port = 5000

    payload = generate_payload(ticks, latitude, longitude, vel, direct)
    json_payload = json.dumps(payload).encode('utf-8')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.sendto(json_payload, (broadcast_address, port))
    print("Sent payload " + str(payload))

    sock.close()


# this is an example. In the final version, the send_cam should be called by
# a function that has access to the actual value
latitude = 47.66772486666667
longitude = 9.170437583333333
while True:
    latitude += 0.001
    longitude += 0.001
    send_cam_udp(0, latitude, longitude ,0 ,"north")
    time.sleep(0.5)
#send_cam_broadcast(0, 0, 0 ,0 ,"north")