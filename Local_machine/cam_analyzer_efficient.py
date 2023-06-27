import json
import socket
import matplotlib.pyplot as plt
import time
import select
import folium
import os
from selenium import webdriver


class UDPPositionPlotter:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.ticks = []
        self.latitude = []
        self.longitude = []
        self.timestamps = []
        self.tstart = time.time()

        plt.ion()
    
    def receive_data(self):
        fig, ax = plt.subplots()
        
        while True:
            ready, _, _ = select.select([self.sock], [], [], 0.2)

            if ready:
                data, addr = self.sock.recvfrom(1024)
                t_elapsed = time.time() - self.tstart
                json_data = data.decode('utf-8')
                payload = json.loads(json_data)

                print("received payload:")
                print(payload)
                print("")

                #Extract JSON
                with open('../cam_msg.json') as file:
                    template_payload = json.load(file)

                # Populate values from received payload
                template_payload['position']['ticks'] = payload['position']['ticks']
                template_payload['position']['latitude'] = payload['position']['latitude']
                template_payload['position']['longitude'] = payload['position']['longitude']
                template_payload['velocity'] = payload['velocity']
                template_payload['direction'] = payload['direction']

                #append to position lists
                self.ticks.append(template_payload['position']['ticks'])
                self.latitude.append(template_payload['position']['latitude'])
                self.longitude.append(template_payload['position']['longitude'])
                self.timestamps.append(t_elapsed)
                #print("lat:", self.latitude[-1])
                #print("long:", self.longitude[-1])
                self.update_map(self.latitude[-1], self.longitude[-1])
                driver.refresh()
                #Clear previous plot and redraw
                ax.clear()
                ax.plot(self.timestamps, self.ticks, label='ticks')
                ax.plot(self.timestamps, self.latitude, label='latitude')
                ax.plot(self.timestamps, self.longitude, label='longitude')
                ax.set_xlabel('Time')
                ax.set_ylabel('Position')
                ax.legend()
                plt.draw()
                # required for updating plot
                plt.pause(0.001)

    def update_map(self, latitude, longitude):
        map = folium.Map(location=[latitude, longitude], zoom_start=18)
        folium.Marker([latitude, longitude], popup = 'car').add_to(map)
        map.location = (latitude, longitude)   
        map.save('map.html')

    def close(self):
        self.sock.close()

# RNPI2 broadcast Address is 10.255.255.255
position_plotter = UDPPositionPlotter('0.0.0.0', 5000)
#position_plotter = UDPPositionPlotter('127.0.0.1', 5000)

try:
    x = os.path.abspath("map.html")
    driver = webdriver.Firefox()
    driver.get("file://" + x)
    position_plotter.receive_data()
except KeyboardInterrupt:
    pass
finally:
    position_plotter.close()