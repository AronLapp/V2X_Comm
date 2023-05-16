import json
import socket
import matplotlib.pyplot as plt
import time

positions_x = []
positions_y = []
positions_z = []
timestamps = []

host = '127.0.0.1'
port = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((host, port))

print("UDP Server is listening on {}:{}".format(host, port))

tstart = time.time()

while True:
    data, addr = sock.recvfrom(1024)
    tElapsed = time.time() - tstart
    json_data = data.decode('utf-8')
    payload = json.loads(json_data)

    #Extract JSON
    position_x = payload['position']['position_x']
    position_y = payload['position']['position_y']
    position_z = payload['position']['position_z']

    #append to position lists
    positions_x.append(position_x)
    positions_y.append(position_y)
    positions_z.append(position_z)
    timestamps.append(tElapsed)

    #Plot positions over time
    plt.plot(timestamps, positions_x, label = 'PosX')
    plt.plot(timestamps, positions_y, label = 'PosY')
    plt.plot(timestamps, positions_z, label = 'PosZ')
    plt.xlabel('Time')
    plt.ylabel('Position')
    plt.legend()
    plt.show()

sock.close()
