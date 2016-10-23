#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-

'''
Created on Oct 12, 2016
@author:     King1600
@summary:    KBot in all
'''

import os
import sys
import time
import random
import discord
import asyncio
from messages import *
from constants import *
from DiscordBot import DiscordBot
from _urbandict import UrbanDictionary
from _youtube import YoutubeExtractor
from _cleverbot import Cleverbot
from _hastebin import Hastebin
from _urlshort import UrlShortener

# add these:
# google url shotener
# insults
# hastebin commands
# anime api

bot = discord.Client()

class KBot(DiscordBot):
    ''' Full Discord KBot '''
    
    def __init__(self):
        super(KBot, self).__init__(bot)
        
        # apis
        self.urbandict = UrbanDictionary(self.session)
        self.shortener = UrlShortener(self)
        self.youtube   = YoutubeExtractor(self)
        self.cleverbot = Cleverbot(self.session)
        self.hastebin  = Hastebin(self.session)
        
    async def on_message(self, msg):
        ''' handle messages '''
        
        # get message info
        channel = msg.channel
        user    = await bot.get_user_info(msg.author.id)
        data    = msg.content
        toKill  = False
        hasRun  = False
        ping    = 0
        
        # onlt perform actions when bot is ready
        if not self.isReady: return
        
        # bot shouldn't response to itself
        if msg.author == self.user: return
        
        # ignore command if chose to do so
        if '@ignore' in data.lower(): return
        
        # record ping if on command
        if '@debug' in data:
            ping = time.time()
            data = data.replace('@debug','')
        
        # on admin
        if self.adminOnly:
            if user != self.owner: hasRun = True
            
        # on filter
        await self.filterBadWords(channel, user, msg, data)
        
        ######### Message Reactions ############
        if 'notice me s' in data and not hasRun:
            try:
                output = ON_NOTICE_ME.format(user.name)
                
                if ping != 0:
                    elapsed = int((time.time() - ping) * 1000.)
                    output += "\n```" + str(elapsed) + "ms```"
                
                await bot.send_message(user, output)
                hasRun = True
            except Exception as error:
                errorString = "Notice me error! " + str(error)
                self.log(errorString)
                await bot.send_message(channel, errorString)
                hasRun = True
                
        elif 'whos ur' in data.lower() and not hasRun:
            otherString = ''.join(data.split('whos ur')[1:])
            if 'bot' in otherString:
                adj = otherString.split('bot')[0]
                adj = [s for s in adj.split() if not s.isspace()]
                adj = [s for s in adj if s != '']
                adj = ' '.join(adj)
                
                if user == self.owner:
                    output = WHOS_UR_TRUE.format(adj, user.name)
                else:
                    output = WHOS_UR_FALSE.format(user.name)
                    
                if ping != 0:
                    elapsed = int((time.time() - ping) * 1000.)
                    output += "\n```" + str(elapsed) + "ms```"
                    
                await bot.send_message(channel, output)
                hasRun = True
                
        else:
            pass
        
        try:
            # try to cleverbot :v
            if not data.startswith(self.prefix) and not hasRun:
                # decide to use cleverbot or not
                useCleverbot = False
                selfID   = "<@" + str(self.user.id) + ">"
                selfNick = "<@!" + str(self.user.id) + ">"
                words    = data.split()
                for word in words:
                    if selfID == word or selfNick == word:
                        useCleverbot = True
                        break
                chance = await self.decision(RESPOND_CHANCE)
                if chance: useCleverbot = True
                
                # if has cleverbot, do response
                if useCleverbot and not self.isQuiet:
                    # string reforming
                    args = data.split()
                    if args[0] in [selfID, selfNick]: args.pop(0)
                    if args[-1] in [selfID, selfNick]: args.pop(-1)
                    for x in range(len(args)):
                        if args[x] in [selfID, selfNick]:
                            args[x] = 'bot'
                        
                    question = ' '.join(args)
                    await bot.send_typing(channel)
                    cleverResponse = await self.cleverbot.ask(question)
                    
                    # alexis mod
                    if user.id == "230716794212581376":
                        atAlexis = "<@" + "230716794212581376" + ">"
                        cleverResponse = atAlexis + " " + cleverResponse
                    
                    if ping != 0:
                        elapsed = int((time.time() - ping) * 1000.)
                        cleverResponse += "\n```" + str(elapsed) + "ms```"
                    await bot.send_message(channel, cleverResponse)
                    hasRun = True
            
            await self.processCommands(user, channel, 
                        msg, data, toKill, hasRun, ping)
        except Exception as error:
            errorString = "Uh oh: " + str(error)
            self.log(errorString)
            await bot.send_typing(channel)
            await bot.send_message(channel, errorString)
        
    async def decision(self, probability):
        ''' generate probability '''
        return random.random() < (probability / 100.)   
    
    #### Process if / else statements ####
        
    async def processCommands(self, user, channel, msg, data, toKill, hasRun, ping):
        ''' process commands given to bot '''
        if data.startswith(self.prefix) and not hasRun:
            # log command
            logMessage = '{0.author.name}> {0.content}'.format(msg)
            self.log(logMessage)
            
            data = data[1:]     # remove prefix
            args = data.split() # command arguments
            out  = None         # bot output variable
            
            if data.startswith('define'):
                ''' urban dictionary define '''
                await bot.send_typing(channel)
                phrase = ' '.join(data.split()[1:])
                out    = await self.urbandict.define(phrase)
                out    = phrase + " : " + out
                out    = out[:CHAR_LIMIT]
                
            elif data.startswith('insult'):
                ''' generate an insult '''
                out = await self.urbandict.generateInsult()
            
            elif data.startswith('help'):
                ''' generate and display hastebin link to commands '''
                link = await self.hastebin.generate(self.cmdInfo)
                out  = "Command list: \n" + str(link)
        
            elif data.startswith('ping'):
                ''' send ping message '''
                out = ON_PING
                
            elif data.startswith('join'):
                ''' create join link '''
                inviteLink = JOIN_LINK.format(id=self.user.id)
                out        = ON_JOIN.format(inviteLink)
                
            elif data.startswith('admin'):
                ''' set admin only for commands '''
                if user != self.owner: out = ON_NOT_OWNER
                else:
                    try:
                        setting = args[1]
                        
                        # enable
                        for c in ONS:
                            if c in setting.lower():
                                self.adminOnly = True
                                out = ON_ADMIN_ENABLE.format(user.name)
                                break
                        
                        # disable
                        for c in OFFS:
                            if c in setting.lower():
                                self.adminOnly = False
                                out = ON_ADMIN_DISABLE
                                break
                            
                        # nothing
                        if out == None:
                            out = ON_BAD_COMMAND
                    except:
                        pass
                
            elif data.startswith('restart'):
                ''' restart bot '''
                if user != self.owner:
                    out = ON_SLEEP_FALSE.format(user.name)
                else:
                    if os.path.exists(BOT_PATH): os.remove(BOT_PATH)
                    with open(BOT_PATH, 'w') as f: f.write('restart=True')
                    out = ON_RESTART
                    toKill = True
            
            elif data.startswith('shutdown'):
                ''' shutdown bot '''
                if user != self.owner:
                    out = ON_SLEEP_FALSE.format(user.name)
                else:
                    if os.path.exists(BOT_PATH): os.remove(BOT_PATH)
                    out = ON_SHUTDOWN
                    toKill = True
                    
            elif data.startswith('clean'):
                ''' clean messages '''
                try:
                    # get settings
                    count  = 0
                    limit  = DELETE_LIMIT
                    amount = int(args[1])
                    if limit < amount: limit = amount
                    if 'silent' in data or 'quiet' in data:
                        silent = True
                    else:
                        silent = False
                        
                    # get users to clean
                    usersToClean = []
                    for word in args:
                        if word.startswith('<@') and word.endswith('>'): 
                            userID = word[2:-1]
                            if userID[0] == '!': userID = userID[1:]
                            newUser = await bot.get_user_info(userID)
                            usersToClean.append(newUser)
                    lowered = data.lower()
                    if 'me' in lowered or 'self' in lowered:
                        if user not in usersToClean:
                            usersToClean.append(user)
                    
                    # clean messages
                    await bot.delete_message(msg)
                    prevMessages = []
                    async for message in bot.logs_from(channel, limit=limit):
                        if message.author == self.user:
                            prevMessages.append(message)
                            count += 1
                        for u in usersToClean:
                            if message.author == u:
                                prevMessages.append(message)
                                count += 1
                        if count >= amount: break
                    await bot.delete_messages(prevMessages)
                        
                    # make output
                    if not silent:
                        await bot.send_typing(channel)
                        out = ON_CLEAN
                        
                except Exception as error:
                    errorString = ON_CLEAN_ERROR.format(str(error))
                    self.log(errorString)
                    
            elif data.startswith('filter'):
                pass
            
            elif data.startswith('shush'):
                self.isQuiet = True
                out = ON_QUIET_ON
                
            elif data.startswith('talk'):
                self.isQuiet = False
                out = ON_QUIET_OFF
            
            elif data.startswith('shorten'):
                ''' shorten url using goo.gl '''
                await bot.send_typing(channel)
                url = args[1].lower()
                if url.startswith('http') or url.startswith('www'):
                    newUrl = await self.shortener.shortenUrl(url)
                    await bot.delete_message(msg)
                    out = "Teeny tiny: " + newUrl
                else:
                    out = "Give me a web link u scrub <.<"
                
            
            elif data.startswith('youtube'):
                ''' built-in youtube info fetcher '''
                await bot.send_typing(channel)
                
                args.pop(0) # get rid of the /youtube parameter
                kargs = {} # command argument dict
                
                if args[0].lower().split(ARGS_SPLIT)[0] not in YOUTUBE_MODES:
                    out = args[0].lower() + " mode doesn't exists"
                    
                else:
                    # set mode
                    try: kargs['modes'] = args[0].lower().split(ARGS_SPLIT)
                    except: pass
                    
                    # set kargs values
                    for pos, arg in enumerate(args):
                        arg = arg.lower()
                        if arg.startswith('search'):
                            query = ' '.join(args[pos:])
                            query = ':'.join(query.split(':')[1:])
                            kargs['search'] = query
                            break
                        else:
                            key   = arg.split(":")[0]
                            value = ':'.join(arg.split(":")[1:])
                            kargs[key] = value
                    
                    # get link if not search
                    if 'url' not in kargs and 'search' not in kargs:
                        kargs['url'] = args[-1] 
                        
                    # get output value from parse
                    out = await self.youtube.argParse(kargs)
            else:
                pass
            
            if out != None and not out.isspace():
                if ping != 0:
                    elapsed = int((time.time() - ping) * 1000.)
                    out += "\n```" + str(elapsed) + "ms```"
                await bot.send_typing(channel)
                await bot.send_message(channel, out)
                
            if toKill:
                self.config["lastChannel"] = str(channel.id)
                await self.quit()
        
    async def on_ready(self):
        ''' set bot variables and run '''
        self.user  = bot.user
        self.owner = await bot.get_user_info(self.ownerId)
        self.log("Logged in as " + str(self.user.id))
        
        # start cleverbot
        await self.cleverbot.init()
        
        # notify last channel it was in
        channelId = self.config["lastChannel"]
        if channelId != '' and not channelId.isspace():
            try:
                channel = bot.get_channel(channelId)
                if channel is not None:
                    await bot.send_message(channel, ON_RETURN)
            except Exception as error:
                self.log("Ready error: " + str(error))
        self.isReady = True
            
    async def filterBadWords(self, channel, user, msg ,data):
        ''' filter out bad words when filter is on '''
        if self.filterInfo[0]:
            filterChannel = self.filterInfo[1]
            if filterChannel != None:
                if channel == filterChannel:
                    remove = False
                    for word in data.split():
                        for char in BAD_WORDS:
                            if char in word.lower():
                                remove = True
                                break
                        if remove: break
                    if remove:
                        response = random.choice(FILTER_RESPONSES)
                        response = response.format(user.name)
                        await bot.delete_message(msg)
                        await bot.send_message(channel, response)

def main():
    global bot
    kbot = KBot()
    
    @bot.event
    async def on_ready():
        await kbot.on_ready()
    
    @bot.event
    async def on_message(message):
        await kbot.on_message(message)
    
    kbot.run()

if __name__ == "__main__":
    main()
    sys.exit()