
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
AUTH = "9ff7813fb8fc6b53cb2a7101875e85e8"

# Up to 12 Clients can be used. But all buttons must be filled
CLIENTS = [
["Ecospend", 165981673, (255,0,0)],
["Ohpen", 156584840, (255,127,0)],
["Amberscript", 167653344, (255,255,0)],
["Something Ventured", 167653396, (0,255,0)],
["Whering", 167653351, (0,149,77)],
["BabyDuet", 161637546, (45,200,77)],
["New Options", 167653385,(7,175,212)],
["Gravity", 164655916,(0,0,255)],
["Dotiv", 167653496, (0,0,255)],
["OneE", 167653362, (224,60,49)],
["Mum", 157881720, (174,118,163)],
["Nothing Ventured", 167653389,(209,187,215)],
# The last 4 buttons are assigned to tags which do not carry an ID
["Admin", 0, (255,255,255)],
["Planning", 0, (255,255,255)],
["Meetings & Calls", 0, (255,255,255)],
["Media", 0,(255,255,255)],
# Final element is a Default tag can be customised as desired.
[""]
]

# Initiate variables
ON = [False] * 12
id = 0
tag = 16

# this will be called when button events are received
def blink(event):
    global id
    global tag
    
    # Button is for a tag
    if event.edge == NeoTrellis.EDGE_RISING and event.number > 11:
        if True in ON:
            if tag == event.number:
                #No tags currently so reset to default tag
                tag = 16
                trellis.pixels[event.number] = OFF
            else:
                for i in range(3):
                    trellis.pixels[event.number] = CLIENTS[event.number][2]
                    time.sleep(0.2)
                    trellis.pixels[event.number] = OFF
                    time.sleep(0.2)
        else:
            # Check if current tag is being turned off
            if tag == event.number:
                #No tags currently so reset to default tag
                tag = 16
                trellis.pixels[event.number] = OFF
            # Else it's a new tag
            else:
                # Turn off the tag button light UNLESS it is default
                if tag != 16:
                    trellis.pixels[tag] = OFF
                tag = event.number
                # Set correct color for Tag
                trellis.pixels[event.number] = CLIENTS[event.number][2]
    #Button is for a project       
    else:    
        # if  button is not already on
        if event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == False:
            # Check for already running timers
            if True in ON:
                trellis.pixels[ON.index(True)] = OFF
                ON[ON.index(True)] = False
                headers = {
                'Content-Type': 'application/json',
                }
                requests.put((f'https://api.track.toggl.com/api/v8/time_entries/{id}/stop'), headers=headers, auth=(f'{AUTH}', 'api_token'))
                    
            trellis.pixels[event.number] = CLIENTS[event.number][2]
            ON[event.number] = True

            # This starts a timer
            headers = {
                'Content-Type': 'application/json',
            }

            data = '''{"time_entry":{
            "tags":["%s"],
            "pid":"%s",
            "created_with":"toggl-box"}}'''%(CLIENTS[tag][0] ,CLIENTS[event.number][1])
            
                   
            response = requests.post('https://api.track.toggl.com/api/v8/time_entries/start', headers=headers, data=data, auth=(f'{AUTH}', 'api_token'))
            id = response.json()['data']['id']


        elif event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == True:
            trellis.pixels[event.number] = OFF
            trellis.pixels[tag] = OFF
            tag = 16
            ON[event.number] = False
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

print("Initialized")

while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)
