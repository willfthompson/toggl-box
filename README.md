# Toggl.Box

Toggle.Box is a real-world implementation of the [Toggl Track](https://toggl.com/track/) tool. Designed to allow tracking of up to 12 projects with 4 separate tags. Select a tag by pressing one of the bottom row of buttons. Then start a timer by pressing any of the top 3 rows. Stop the timer by either pressing that button again, or starting a new timer with the same process.

This was mostly a fun project, designed to make using Toggl a more memorable process.

# Customisation & Use

First you'll need to find you Toggl API Token, which can be found under the "My Profile" tab in your Toggl account. Assign this to the AUTH variable.

Once customised the project can be run directly from the console using Python 3, and will run continuously until interrupted meaning you can unplug monitors etc from your Pi if you wish.

  # Finidng Project IDs
  The process for finding project IDs is not made simple by Toggl. I built a basic script that will pull your projects and print their ids to the console. Run         pid_finder.py from the console.

  Keep a note of these, or keep the console window open as you'll need them to configure your buttons.
  
  # Customising Buttons
  The CLIENTS array contains all the information required for each button. 

  Element 0 – The name of the button. In the case of Projects, this is just for your reference, in the case of tags this information is passed directly to Toggl.

  Element 1 – The ID for the timer. This is where you add the PIDs you just pulled.

  Element 2 – The RGB color for the button. This can be replaced with any of the default color definitions if you prefer.

  The Array corresponds directly to the button matrix. So add your projects in the order you wish them to appear on the buttons – e.g Element 0 is the top left       button, Element 15 is the bottom right.
  
# Failsafes

If the timer is not able to be started, the pressed button will flash and then switch off if an error occurs.  This is triggered by an error response from Toggl's server, the console will print this error for debugging.

# Current Limitations

It is possible to tile NeoTrellis boards to increase the number of available hardware buttons, however this implementation was designed specifically for a single NeoTrellis board supporting 16 buttons.  Some minor tweaks to the code will be required if you wish to use more, this feature may be added later if I need it.
