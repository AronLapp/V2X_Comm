# Module V2X Communication HTWG Konstanz SS23
## CAM Communication
Implementation of a simple CAM (Cooperative Awareness Message) that holds the vehicle's position, velocity and direction. The message should be sent via network and received by either a UDP channel or a broadcas message (everyone on the network can read it).<br/>cam_analyzer.py is meant to be ran on a seperate computer that is in the same network as the model car. It listens to broadcasted CAMs and creates a plot of the car's coordinates over time.
# Modules
## Local_machine/cam_analyzer_efficient.py
All 0.2 seconds, new CAM messages are fetched (value is modifiable). By default, the frequency of incoming messages is set to 1Hz but can be increased in PiCar/payload_crafter.py.<br/>The fetched JSON messages are unpacked and the positions are plotted over time. The Plot refreshes itself whenever new data is displayed. At this point, the only relevant Plot is Pos_X as it is the only value that is changed in PiCar/payload_crafter.py<br/>
## PiCar/cam_sender.py
Simple script that can send UDP and broadcast messages for debugging purposes
## PiCar/payload_crafter.py
The script reads the hall sensor after a fixed interval, evaluates whether the HALL sensor's output value has changed and evaluates the position accordingly. Every second, the actual velocity is evaluated by dividing the positional change by the time interval. After that, all data is packed into a JSON messaged and sent via broadcast.
## PiCar/payload_crafter_interrupt.py
Similar to the payload_crafter.py script, the script generates real_time measurements of position and velocity. This version uses GPIO callbacks to increase accurracy and make sure no measurements are missed whicch is possible using the time interrups in payload_crafter.py.