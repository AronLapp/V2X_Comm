from time import sleep
import RPi.GPIO as GPIO
import json
import socket

GPIO.setmode(GPIO.BCM)

INPUT_PIN = 4
GPIO.setup(INPUT_PIN, GPIO.IN)

def listen():
    if(GPIO.input(INPUT_PIN) == True):
        return 3.3
    else:
        return 0.0

# Note: Can not track direction at this point
def position_tracker(posold, listenold, listenval):
    if len(posold) >= 1:
        if listenval == listenold:
            return posold
        else:
            return posold + 0.5

def calculate_velocity(velarr):
    if(len(velarr)) > 1:
        currvel = velarr[len(velarr - 1)] - velarr[0]
        return currvel
    else:
        return 0

def generate_payload(posx, posy, posz, vel, direct):
    with open('cam_msg.json') as file:
        template_payload = json.load(file)

        template_payload['position']['position_x'] = posx
        template_payload['position']['position_y'] = posy
        template_payload['position']['position_z'] = posz
        template_payload['velocity'] = vel
        template_payload['direction'] = direct
    payload = template_payload
    return payload

def send_cam_broadcast(posx, posy, posz, vel, direct):
    # requires actual values
    broadcast_address = '10.255.255.255'
    port = 5000

    payload = generate_payload(posx, posy, posz, vel, direct)
    json_payload = json.dumps(payload).encode('utf-8')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.sendto(json_payload, (broadcast_address, port))

    sock.close()

listenold = -1
posarr = []
for i in range(0, 5):
    listenval = listen()
    position_tracker(posarr, listenval, listenold)
    listenold = listenval