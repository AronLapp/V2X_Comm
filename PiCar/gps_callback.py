import RPi.GPIO as GPIO
import json
import socket
import serial
from array import *
from time import sleep, time

import pynmea2
import math
import re

# GPS code is largely extracted from https://www.waveshare.com/wiki/EM060K-GL_LTE_Cat-6_HAT examples EM06E_GNSS_GAODE.py
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # Semi-major axis
ee = 0.00669342162296594323  # Eccentricity squared

# MAX_POSITIONS = 1/interval
MAX_POSITIONS = 50
INPUT_PIN = 4
ELAPSED_TIME_THRESHOLD = 1.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN)

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

def serial_data_reader():
    ser = serial.Serial("/dev/ttyUSB1", 115200)
    #print("Serial port opened")
    while True:
        line = str(ser.readline(),encoding = "utf-8")
        print("starts with $GPRMC")
        if line.startswith("$GPRMC"):
            global Longitude
            global Latitude
            rmc = pynmea2.parse(line)
            if re.match("^\d+?\.\d+?$", rmc.lat)is not None:
                print(rmc)
                latitude = rmc.latitude
                longitude= rmc.longitude
                return [longitude, latitude]
        #time.sleep(2)
    return [-1, -1]

def setup():
    # global response
    ser2 = serial.Serial("/dev/ttyUSB2",115200)
    print("ttyUSB2 Open!!!")
    ser2.write('AT+QGPS=1\r'.encode())
    print("AT+QGPS=1")
    ser2.close()
    print("ttyUSB2 Close!!!")

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

setup()
listen_callback()
latitude = 0
longitude = 0
while True:
    current_time = time()
    elapsed_time = current_time - start_time
    gps_data = serial_data_reader()
    new_latitude = gps_data[0]
    new_longitude = gps_data[1]
    if new_latitude == -1 and new_longitude == -1:
        pass
    else:
        latitude = new_latitude
        longitude = new_longitude
        if elapsed_time >= ELAPSED_TIME_THRESHOLD:
            velocity = update_Velocity(Pos)
        # Coordinate system and Direction not implemented yet
            send_cam_broadcast(ticks = Pos[-1], latitude = latitude, longitude = longitude , vel = velocity, direct = 'forward')
            Pos = [Pos[-1]]
            start_time = time()
