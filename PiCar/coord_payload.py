import RPi.GPIO as GPIO
import json
import socket
from array import * # FIFO array
from time import sleep, time
import serial
import pynmea2
import re
import math

 
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # Semi-major axis
ee = 0.00669342162296594323  # Eccentricity squared

# MAX_POSITIONS = 1/interval
MAX_POSITIONS = 50
INPUT_PIN = 4
ELAPSED_TIME_THRESHOLD = 1.0
GPS_LISTEN_TIMER = 0.2

GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN)

def _transformlng(longitude, latitude):
    ret = 300.0 + longitude + 2.0 * latitude + 0.1 * longitude * longitude + \
          0.1 * longitude * latitude + 0.1 * math.sqrt(math.fabs(longitude))
    ret += (20.0 * math.sin(6.0 * longitude * pi) + 20.0 *
            math.sin(2.0 * longitude * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(longitude * pi) + 40.0 *
            math.sin(longitude / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(longitude / 12.0 * pi) + 300.0 *
            math.sin(longitude / 30.0 * pi)) * 2.0 / 3.0
    return ret
 
def _transformlat(longitude, latitude):
    ret = -100.0 + 2.0 * longitude + 3.0 * latitude + 0.2 * latitude * latitude + \
          0.1 * longitude * latitude + 0.2 * math.sqrt(math.fabs(longitude))
    ret += (20.0 * math.sin(6.0 * longitude * pi) + 20.0 *
            math.sin(2.0 * longitude * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(latitude * pi) + 40.0 *
            math.sin(latitude / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(latitude / 12.0 * pi) + 320 *
            math.sin(latitude * pi / 30.0)) * 2.0 / 3.0
    return ret

def update_Velocity(Pos_arr):
    if len(Pos_arr) >= 2:
        delta_pos = Pos_arr[-1] - Pos_arr[0]
        elapsed_time = 1.0
        velocity = delta_pos / elapsed_time
        return velocity
    else:
        return 0.0
    
def listen_callback():
    GPIO.add_event_detect(INPUT_PIN, edge = GPIO.FALLING, callback= falling_edge_callback, bouncetime = 1)

def falling_edge_callback(channel):
    Pos.append(Pos[-1] + .5)    

def gps_callback():
    mglat = -1
    mglng = -1
    global ser1
    ser1 = serial.Serial("/dev/ttyUSB1", 115200)
    line = str(ser1.readline(),encoding='utf-8')
    if line.startswith("$GPRMC"):
        rmc = pynmea2.parse(line)
        if re.match("^\d+?\.\d+?$", rmc.lat)is not None:
            print(rmc)
            latitude = rmc.latitude
            longitude= rmc.longitude
            dlat = _transformlat(longitude - 105.0, latitude - 35.0)
            dlng = _transformlng(longitude - 105.0, latitude - 35.0)
            radlat = latitude / 180.0 * pi
            magic = math.sin(radlat)
            magic = 1 - ee * magic * magic
            sqrtmagic = math.sqrt(magic)
            dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
            dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
            mglat = latitude + dlat
            mglng = longitude + dlng
    return [mglat, mglng]

Pos = [0]
start_time = time()

def generate_payload(ticks, latitude, longitude, vel, direct):
    with open('cam_msg.json') as file:
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

global latitude
global longitude


ser2 = serial.Serial("/dev/ttyUSB2",115200)
print("ttyUSB2 Open!!!")
ser2.write('AT+QGPS=1\r'.encode())
print("AT+QGPS=1")
ser2.close()
print("ttyUSB2 Close!!!")

listen_callback()
while True:
    latitude = -1
    longitude = -1
    current_time = time()
    
    elapsed_time = current_time - start_time
    if elapsed_time % GPS_LISTEN_TIMER < 0.1:
        actualgps = gps_callback()
    
    if elapsed_time >= ELAPSED_TIME_THRESHOLD:
        print("Latutide: ", latitude, " Longitude",  longitude, "\n")
        velocity = update_Velocity(Pos)
        # Coordinate system and Direction not implemented yet
        send_cam_broadcast(ticks = Pos[-1], latitude = actualgps[0], longitude = actualgps[1] , vel = velocity, direct = 'forward')
        Pos = [Pos[-1]]
        start_time = time()
