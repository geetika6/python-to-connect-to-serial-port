##this is the main file which starts the pygame gui ,clock etc.It calls the Config class which instantiaties the various configurations of the application.It then waits for the events and calls the respective mode to run the event handling code.It generates a laoding image when there is a delay in switching from one mode/view to another.It deallocates the memory acquired for the views, widgets, etc once the event catching loop exits on account of error or when the user exits.
import sys
import const
import logging
from math import *
from scope_single_analog import ScopeSingleAnalog
def quit_prog():
    sys.exit()
scope_h=ScopeSingleAnalog()    
def main():
    running=True
    count=1
    while(running == True):
        #clock.tick(fps)
        update=scope_h.update()
        count+=1
        if count==10:
             running =False

    #quit_prog()
    
# Run the thing!
main()
