import json
import socket


def send_cam(posx, posy, posz, vel, direct):
    host = "127.0.0.1"
    port = 5000

    with open('cam_msg.json') as file:
        template_payload = json.load(file)

    template_payload['position']['position_x'] = posx
    template_payload['position']['position_y'] = posy
    template_payload['position']['position_z'] = posz
    template_payload['velocity'] = vel
    template_payload['direction'] = direct

    payload = template_payload
    # convert payload into json, json into bytes
    json_payload = json.dumps(payload).encode('utf-8')


    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send UDP packet
    sock.sendto(json_payload, (host, port))
    print("Sent payload " + str(payload))

    sock.close()

# this is an example. In the final version, the send_cam should be called by
# a function that has access to the actual values
send_cam(0, 0, 0 ,50 ,"north")