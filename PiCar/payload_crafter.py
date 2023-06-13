import RPi.GPIO as GPIO
import json
import socket
from array import * # FIFO array
from time import sleep, time

# MAX_POSITIONS = 1/interval
MAX_POSITIONS = 50
INPUT_PIN = 4
ELAPSED_TIME_THRESHOLD = 1.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN)

def read_HALL():
    if(GPIO.input(INPUT_PIN) == True):
        return 3.3
    else:
        return 0.0

def update_Pos_List(old_HALL, HALL, Pos):
    if old_HALL == HALL:
        Pos.append(Pos[-1])
        Pos = truncate_list(Pos)
        return Pos
    else:
        Pos.append(Pos[-1] + 0.5)
        Pos = truncate_list(Pos)
        return Pos

def truncate_list(lst):
    while len(lst) > MAX_POSITIONS:
        lst.pop(0)
    return lst

def update_Velocity(Pos_arr):
    if len(Pos_arr) >= 2:
        delta_pos = Pos_arr[-1] - Pos_arr[0]
        elapsed_time = 1.0
        velocity = delta_pos / elapsed_time
        return velocity
    else:
        return 0.0
    
Pos = [0]
old_HALL = -1
start_time = time()

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

def send_cam_broadcast(ticks, latitude, longitude, vel, direct):
    # requires actual values
    broadcast_address = '10.42.0.255'
    port = 5000
    payload = generate_payload(ticks, latitude, longitude, vel, direct)
    json_payload = json.dumps(payload).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(json_payload, (broadcast_address, port))
    sock.close()

while True:
    HALL = read_HALL()
    Pos = update_Pos_List(old_HALL, HALL, Pos)
    old_HALL = HALL
    current_time = time()
    elapsed_time = current_time - start_time

    if elapsed_time >= ELAPSED_TIME_THRESHOLD:
        velocity = update_Velocity(Pos)
        # Coordinate system and Direction not implemented yet
        send_cam_broadcast(ticks = Pos[-1], latitude = 0, longitude = 0 , vel = velocity, direct = 'forward')
        start_time = time()
    
    sleep(0.02)