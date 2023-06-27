# Module V2X Communication HTWG Konstanz SS23
## CAM Communication
Implementation of a simple CAM (Cooperative Awareness Message) that holds the vehicle's position, velocity and direction. The message should be sent via network and received by either a UDP channel or a broadcast message (everyone on the network can read it).<br/>cam_analyzer.py is meant to be ran on a seperate computer that is in the same network as the model car.
# Modules
## Local_machine/cam_analyzer_efficient.py
All 0.2 seconds, new CAM messages are fetched (value is modifiable). By default, the frequency of incoming messages is set to 1Hz but can be increased in PiCar/payload_crafter.py.<br/>The fetched JSON messages are unpacked and the position (ticks of HALL sensor) and GPS latitude and longitude are plotted over time. The Plot refreshes itself whenever new data is displayed.<br/>It listens to broadcasted CAMs and extracts the JSON data. The ticks of the HALL Sensor and the cooridnates are then displayed in a plot:
<br /><br />![](/resource/plot.png "Plot")<br />
Additionally, the Coordinates are displayed on a Map so that the data is more accessible to users:
<br /><br />![](/resource/Map.png "Map")<br />
## PiCar/cam_sender.py
Simple script that can send UDP and broadcast messages for debugging purposes
## PiCar/payload_crafter.py
The script reads the hall sensor after a fixed interval, evaluates whether the HALL sensor's output value has changed and evaluates the position accordingly. Every second, the actual velocity is evaluated by dividing the positional change by the time interval. After that, all data is packed into a JSON messaged and sent via broadcast.
## PiCar/payload_crafter_callback.py
Similar to the payload_crafter.py script, the script generates real_time measurements of position and velocity. This version uses GPIO callbacks to increase accurracy and make sure no measurements are missed whicch is possible using the time interrups in payload_crafter.py.
## PiCar/coord_payload.py
coord_payload extends the payload_crafter_callback by adding GPS data to the payload. While the HALL sensor is updated via callback, the GPS sensor's data is updated in a loop that checks for new data on the serial console. The data then is extracted and added to the payload.json that is sent.