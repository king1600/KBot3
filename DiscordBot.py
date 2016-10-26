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
    filterInfo = {}
    
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
        
        # load opus for audio
        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus')
        
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
        task = None
        try:
            asyncio.set_event_loop(self.loop)
            try:
                #self.loop.run_until_complete(self.start())
                task = asyncio.Task(self.start())
                self.loop.run_forever()
            except:
                self.loop.run_until_complete(self.bot.logout())
        except Exception as e:
            print(str(e))
            
        # close all tasks and loop
        if task is not None: task.cancel()
        pending = asyncio.Task.all_tasks(self.loop)
        for _task in pending:
            try: _task.cancel_all()
            except: pass
        self.loop.close()
            
        # emit exit event
        self.exitEvent.set()
        
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
        self.loop.stop()