
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
AUTH = "Your Auth code"

# Up to 12 Clients can be used. But all buttons must be filled
CLIENTS = [
["name", 0000000000, (255,0,0)],
["name", 000000000, (255,127,0)],
["name", 000000000, (255,255,0)],
["name", 00000000, (0,255,0)],
["name", 00000000, (0,149,77)],
["name", 00000000, (45,200,77)],
["name", 00000000,(7,175,212)],
["name", 00000000,(0,0,255)],
["name", 00000000, (0,0,255)],
["name", 00000000, (224,60,49)],
["name", 00000000, (176,8,143)],
["name", 00000000,(255,188,0)],
# The last 4 buttons are assigned to tags which do not carry an ID
["Admin", 0, (255,255,255)],
["Planning", 0, (255,255,255)],
["Meetings & Calls", 0, (255,255,255)],
["Doing", 0,(255,255,255)],
# Final element is a Default tag can be customised as desired.
[""]
]

# Initiate variables
ON = [False] * 12
id = 0
tag = 16

# this will be called on incorrect inputs to flash the requested button at the assigned color
def flash(e):
    for i in range(3):
        trellis.pixels[e] = CLIENTS[e][2]
        time.sleep(0.1)
        trellis.pixels[e] = OFF
        time.sleep(0.1)

#This will be called when the tag should be reset to default
def defaulttag(e):
    tag = 16
    trellis.pixels[e] = OFF

#Will be called when a timer stop needs to be sent to Toggl
def stoptimer(e):
    global id
    trellis.pixels[e] = OFF
    ON[e] = False
    headers = {
    'Content-Type': 'application/json',
    }
    requests.put((f'https://api.track.toggl.com/api/v8/time_entries/{id}/stop'), headers=headers, auth=(f'{AUTH}', 'api_token'))

def starttimer(e,t):
    global id
    trellis.pixels[e] = CLIENTS[e][2]
    
    # This starts a timer
    headers = {
        'Content-Type': 'application/json',
    }

    data = '''{"time_entry":{
    "tags":["%s"],
    "pid":"%s",
    "created_with":"toggl-box"}}'''%(CLIENTS[t][0] ,CLIENTS[e][1])
                         
    response = requests.post('https://api.track.toggl.com/api/v8/time_entries/start', headers=headers, data=data, auth=(f'{AUTH}', 'api_token'))
    if response.ok:
        ON[e] = True
        id = response.json()['data']['id']
    else:
        print(response.status_code)
        flash(e)
    
# this will be called when button events are received
def blink(event):
    global id
    global tag
    
    # Button is for a tag
    if event.edge == NeoTrellis.EDGE_RISING and event.number > 11:
        if True in ON:
            flash(event.number)
        else:
            # Check if current tag is being turned off
            if tag == event.number:
                #No tags currently so reset to default tag
                defaulttag(event.number)
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
                stoptimer(ON.index(True))
            starttimer(event.number, tag)
        elif event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == True:
            stoptimer(event.number)
            defaulttag(tag) 

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



