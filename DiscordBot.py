#!/usr/bin/env python3
#! python3

'''
Created on Oct 12, 2016
@author:     King1600
@summary:    KBot main functionality
'''

import json
import asyncio
import aiohttp
import discord
import threading

from constants import *

class DiscordBot(object):
    ''' DiscordBot Attributes '''
    # check booleans
    adminOnly  = False
    isReady    = False
    isActive   = True
    isQuiet    = False
    filterInfo = (False, None)
    
    # bot info
    config     = {}
    info       = {}
    
    # async & thread objects
    logMutex   = threading.Lock()
    exitEvent  = threading.Event()
    loop       = None
    
    # discord bot & http session
    bot       = None
    session   = aiohttp.ClientSession()
    
    def __init__(self, botObject):
        ''' start KBot '''
        # set settings
        self.readConfig()
        self.prefix    = self.config["command_prefix"]
        self.token     = self.config["token"]
        self.email     = self.config["email"]
        self.password  = self.config["password"]
        self.ownerId   = self.config["owner"]
        self.googleKey = self.config["google_api_key"]
        
        # read command info
        with open('commands.info','r') as f:
            self.cmdInfo = f.read()
            self.cmdInfo = self.cmdInfo.replace('{PREFIX}', self.prefix)
        
        # get event loop & bot
        self.loop      = asyncio.get_event_loop()
        self.bot       = botObject
        
    def run(self):
        ''' truly start bot '''
        # run until exit event triggered
        self.createThread(self.activateLoop)
        if self.isActive: self.exitEvent.wait()
        
        # quitting bot
        self.writeConfig()
        
    def activateLoop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start())
        except:
            self.loop.run_until_complete(self.bot.logout())
        self.loop.close()
        self.loop.shutdown()
        
    def readConfig(self):
        ''' load config json data '''
        with open(CONF_PATH, 'r') as f:
            self.config = json.loads(f.read())
            
    def writeConfig(self):
        ''' write current config data to file '''
        with open(CONF_PATH, 'w') as f:
            f.write(json.dumps(self.config, indent=4, sort_keys=True))

    def createThread(self, func, *args):
        ''' create a daemon python thread '''
        thread = threading.Thread(target=func, args=args)
        thread.setDaemon(True)
        thread.start()
        return thread

    async def quit(self):
        ''' quit bot '''
        await self.closeAll()
        self.exitEvent.set()
        
    def log(self, obj):
        ''' synchronized logging '''
        self.logMutex.acquire(1)
        if not isinstance(obj, str):
            obj = repr(obj)
        print(obj)
        with open(LOG_PATH, 'a') as f: f.write(obj + "\n")
        self.logMutex.release()
        
    async def start(self):
        ''' connect & login into KBot '''
        try:
            if self.token != '':
                await self.bot.login(self.token)
            else:
                await self.bot.login(self.email, self.password)
            await self.bot.connect()
        except discord.LoginFailure:
            self.log("Failed to login! ")
            self.isActive = False
            self.quit()
        except Exception as e:
            self.log("Login Error: " + str(e))
            self.isActive = False
            self.quit()
            
    
    async def closeAll(self):
        ''' close all objects '''
        await self.bot.logout()
        await self.bot.close()