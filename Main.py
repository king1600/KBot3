#!/usr/bin/env python3
#! python3

'''
Created on Oct 12, 2016
@author:     King1600
@summary:    Run KBot in seperate process to enable restart 
'''

import os
import sys
import subprocess

# Constants
KBOT_FILE  = "Kbot.py"
BOT_CHECK  = "bot.info"
COMMAND    = "{0} {1}".format(sys.executable, KBOT_FILE)
IS_WINDOWS = True if 'nt' in os.name else False
if IS_WINDOWS: CLEAR   = "cls"
else: CLEAR   = "clear"

# main function
def main():
    running = True # bot is running
    
    while running:
        try:
            # run bot
            command = COMMAND.split()
            print(command)
            subprocess.call(command)
            
            # check if restart or shutdown
            if not os.path.exists(BOT_CHECK):
                running = False
                
        # handle ctrl-c and quit
        except KeyboardInterrupt:
            running = False
            break
        
        # clear screen for next bot
        os.system(CLEAR)
    
    sys.exit()

if __name__ == '__main__':
    main()
