import RPi.GPIO as GPIO
import time
import keyboard

# Set up GPIO pins and PWM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
RPWM = 13 # GPIO pin 19 to the RPWM on the BTS7960
LPWM = 12 # GPIO pin 26 to the LPWM on the BTS7960
L_EN = 20 # connect GPIO pin 20 to L_EN on the BTS7960
R_EN = 26 # connect GPIO pin 21 to R_EN on the BTS7960

# set all pins output
GPIO.setup(RPWM, GPIO.OUT)
GPIO.setup(LPWM, GPIO.OUT)
GPIO.setup(L_EN, GPIO.OUT)
GPIO.setup(R_EN, GPIO.OUT)

# left and right enable on HBRidge
GPIO.output(R_EN, True)
GPIO.output(L_EN, True)

rpwm = GPIO.PWM(RPWM, 1000)
lpwm = GPIO.PWM(LPWM, 1000)

rpwm.start(0)
lpwm.start(0)

# Motor control functions
def forward(speed):
    rpwm.ChangeDutyCycle(speed)
    lpwm.ChangeDutyCycle(0)

def backward(speed):
    rpwm.ChangeDutyCycle(0)
    lpwm.ChangeDutyCycle(speed)

def stop():
    rpwm.ChangeDutyCycle(0)
    lpwm.ChangeDutyCycle(0)

# Key press event handler
def on_key_press(event):
    if event.name == 'up':
        forward(100)
    elif event.name == 'down':
        backward(100)
    elif event.name == 'esc':
        stop()

# Register the key press event handler
keyboard.on_press(on_key_press)

# Keep the script running
while True:
    time.sleep(0.1)
