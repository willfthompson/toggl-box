
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
AUTH = "Your Auth Code"

# Up to 12 Clients can be used. But all buttons must be filled
CLIENTS = [
["name", pid goes here, (255,0,0)],
["name", pid goes here, (255,127,0)],
["name", pid goes here, (255,255,0)],
["name", pid goes here, (0,255,0)],
["name", pid goes here, (0,149,77)],
["name", pid goes here, (45,200,77)],
["name", pid goes here,(7,175,212)],
["name", pid goes here,(0,0,255)],
["name", pid goes here, (0,0,255)],
["name", pid goes here, (224,60,49)],
["name", pid goes here, (176,8,143)],
["name", pid goes here,(255,188,0)],
# The last 4 buttons are assigned to tags which do not carry an ID
["Admin", 0, (255,255,255)],
["Planning", 0, (255,255,255)],
["Meetings & Calls", 0, (255,255,255)],
["Doing", 0,(255,255,255)],
# Final element is a Default tag can be customised as desired. This will be attached when no tag is chosen
[""]
]

# Initiate variables
ON = [False] * 12
id = 0
tag = 16

# this will be called on incorrect inputs to flash the requested button at the assigned color
def flash(e):
    trellis.pixels[e] = CLIENTS[e][2]
    time.sleep(0.05)
    trellis.pixels[e] = OFF
    time.sleep(0.05)

#This will be called when the tag should be reset to default
def defaulttag(e):
    global tag
    trellis.pixels[e] = OFF
    tag = 16

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
        #Timer is running
        if True in ON:
            stoptimer(ON.index(True))
            # Pressing same tag again
            if tag == event.number:
                flash(event.number)
                trellis.pixels[event.number] = CLIENTS[event.number][2]
            # A new tag
            else:
                trellis.pixels[tag] = OFF
                tag = event.number
                trellis.pixels[event.number] = CLIENTS[event.number][2]
        #Timer is NOT running
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
        # if this timer is NOT running
        if event.edge == NeoTrellis.EDGE_RISING and ON[event.number] == False:
            # Check for other running timers
            if True in ON:
                stoptimer(ON.index(True))
                defaulttag(tag)
            starttimer(event.number, tag)
        # if this timer is running
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
