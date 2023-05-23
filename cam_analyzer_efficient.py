import json
import socket
import matplotlib.pyplot as plt
import time
import select


class UDPPositionPlotter:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.positions_x = []
        self.positions_y = []
        self.positions_z = []
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
                position_x = payload['position']['position_x']
                position_y = payload['position']['position_y']
                position_z = payload['position']['position_z']

                #append to position lists
                self.positions_x.append(position_x)
                self.positions_y.append(position_y)
                self.positions_z.append(position_z)
                self.timestamps.append(t_elapsed)

                #Clear previous plot and redraw
                ax.clear()
                ax.plot(self.timestamps, self.positions_x, label='PosX')
                ax.plot(self.timestamps, self.positions_y, label='PosY')
                ax.plot(self.timestamps, self.positions_z, label='PosZ')
                ax.set_xlabel('Time')
                ax.set_ylabel('Position')
                ax.legend()
                plt.draw()
                # required for updating plot
                plt.pause(0.001)

    def close(self):
        self.sock.close()

# RNPI2 broadcast Address is 10.255.255.255
position_plotter = UDPPositionPlotter('0.0.0.0', 5000)

try:
    position_plotter.receive_data()
except KeyboardInterrupt:
    pass
finally:
    position_plotter.close()
