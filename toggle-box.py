
import time
import requests

from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis

# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

# create the trellis
trellis = NeoTrellis(i2c_bus)

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

#Toggl Authorisation Goes Here
AUTH = "REDACTED"


# some clients to test
CLIENTS = [
["Admin", 160033931,RED],
["Baby Duet", 161637546,YELLOW],
["Admin", 160033931,GREEN],
["Admin", 160033931,CYAN],
["Admin", 160033931,BLUE],
["Admin", 160033931,PURPLE],
["Admin", 160033931,(125,125,125)],
["Admin", 160033931,(15,125,250)],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED],
["Admin", 160033931,RED]
]

ON = [False] * 16
id = 0

# this will be called when button events are received
def blink(event):
    global id
    # turn the LED on when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == False:
        # Check for already running timers
        if True in ON:
            trellis.pixels[ON.index(True)] = OFF
            ON[ON.index(True)] = False
            headers = {
            'Content-Type': 'application/json',
            }
            requests.put((f'https://api.track.toggl.com/api/v8/time_entries/{id}/stop'), headers=headers, auth=(f'{AUTH}', 'api_token'))
        # Turn on the correct light and start the timer       
        trellis.pixels[event.number] = CLIENTS[event.number][2]
        ON[event.number] = True

        # This starts a timer
        headers = {
            'Content-Type': 'application/json',
        }

        data = '''{"time_entry":{"description":"Meeting with possible clients",
        "tags":["billed"],
        "pid":"%s",
        "created_with":"curl"}}'''%(CLIENTS[event.number][1])
                   
        response = requests.post('https://api.track.toggl.com/api/v8/time_entries/start', headers=headers, data=data, auth=(f'{AUTH}', 'api_token'))
        id = response.json()['data']['id']

    elif event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == True:
        trellis.pixels[event.number] = OFF
        ON[event.number] = False

        #This stops a timer after finding the id of the one just started
        headers = {
            'Content-Type': 'application/json',
        }
        requests.put((f'https://api.track.toggl.com/api/v8/time_entries/{id}/stop'), headers=headers, auth=(f'{AUTH}', 'api_token'))

      

for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

    # cycle the LEDs on startup
    trellis.pixels[i] = CLIENTS[i][2]
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(0.05)

while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)

