#!/usr/bin/env python3
#! python3

'''
Created on Oct 23, 2016
@author:     King1600
@summary:    Music Player
'''

import os
import json
import pafy
import uuid
import time
import shutil
import random
import asyncio
import requests
import tempfile
import constants
import subprocess
from messages import *
from constants import PLAYER_VOLUME, FFMPEG

class VoiceEntry(object):
    ''' voice client for each server '''
    def __init__(self, server_id, voice, channel, main):
        self.server_id   = server_id      # the server id
        self.player      = None           # the stream player
        self.voice       = voice          # the voice client
        self.vChannel    = voice.channel  # the voice channel
        self.channel     = channel        # text channel
        self.isPlaying   = False          # check if playing
        self.queue       = []             # array of youtube urls
        self.currentFile = ""             # path to current audio file
        self.currentSong = ""             # title of current song playing
        self.volume      = PLAYER_VOLUME  # player volume
        
        self.main        = main           # attach to PlayerObject
        self.loop        = asyncio.new_event_loop()
        
    def destroy(self):
        try: self.player.stop()
        except: pass
        self.player = None
       
        self.asyncTask(self.disconnect)
        
    def get_next_song(self):
        try:
            if self.queue != []:
                # download song
                nextSong = self.queue.pop(-1)["url"]
                self.downloadAudio(nextSong)
                
                # create player
                self.player = self.create_player()
                self.player.start()
                self.isPlaying = True
                self.player.volume = self.volume
            else:
                self.isPlaying = False
                
        except Exception as e:
            print("Error in get_next_song -> " + str(e))
    
    ####################################################
    
    def getMetaData(self, url):
        ''' fetch video info from youtube.com/oembed '''
        link = self.main.kbot.youtube.getVideoId(url)
        link = constants.YOUTUBE_LINK.format(id=link)
        link = constants.YOUTUBE_OEMBED.format(url=link)

        response = requests.get(link)
        info = response.text
        return json.loads(info)

        
    def getAudioStream(self, url, fmt='m4a'):
        ''' get audio stream url from video '''
        url = self.main.kbot.youtube.getVideoId(url)
        stream = pafy.new(url, basic=False, gdata=False)
        return stream.getbestaudio(preftype=fmt).url_https
    
    def create_player(self):
        ''' create new stream player '''
        return self.voice.create_ffmpeg_player(
            open(self.currentFile), pipe=True, after=self.get_next_song)
    
    def downloadAudio(self, song):
        ''' download audio and save to file location '''
        try:
            # get song info
            self.currentSong = self.getMetaData(song)
            self.currentSong = self.currentSong['title']
            
            # get audio url and file name
            song = self.getAudioStream(song)
            randFile = os.path.join(self.main.dir, str(uuid.uuid4()))
            
            # download audio
            resp = requests.get(song)
            with open(randFile + ".m4a", 'wb') as f:
                for chunk in resp.iter_content(1024):
                    if chunk: f.write(chunk)
        
            # delete last player
            if self.player is not None:
                try: self.player.stop()
                except: pass
            self.player = None
            if os.path.isfile(self.currentFile):
                try: os.remove(self.currentFile)
                except: pass
        
            # return file
            self.currentFile = randFile + ".m4a"
            return self.currentFile
                
        except Exception as e:
            print("Error in downloadAudio: " + str(e))
    
    ####################################################
                
    def asyncTask(self, function, *args):
        try:
            result = self.loop.run_until_complete(function(*args))
            return result
        except Exception as e:
            print("Error in asyncTask -> " + str(e))
                
    async def disconnect(self):
        ''' disconnect voice channel '''
        await self.voice.disconnect()
    
    async def move_to(self, channel):
        ''' move voice client to another voice channel '''
        await self.voice.move_to(channel)
        
    ############## MUSIC FUNCTIONS #######################
    
    def pause(self):
        try: self.player.pause()
        except: pass
        
    def resume(self):
        try: self.player.resume()
        except: pass
        
    def setVolume(self, vol):
        self.volume = vol / 100.
        try: self.player.volume = self.volume
        except: pass
        
    def skip(self):
        if self.queue != []:
            self.get_next_song()
    
    ######################################################



class Player(object):
    ''' music player to manage playing audio '''
    
    def __init__(self, kbot, bot):
        # create bots
        self.kbot = kbot
        self.bot  = bot
        
        # track voice entries
        self.running = True
        self.clients = {}
        
        # create temp-dir for storing audio files
        sess_dir = "KBot3_"
        self.dir = tempfile.gettempdir()
        self.dir = os.path.join(self.dir, sess_dir)
        try: os.makedirs(self.dir)
        except: pass
        
    def close(self):
        # stop running
        self.running = False
        time.sleep(0.1)
        
        # delete the songs
        try: shutil.rmtree(self.dir)
        except: pass
        
        # kill all the VoiceEntries
        for s_id in self.clients:
            self.clients[s_id].loop.close()
        
    async def summon(self, msg):
        ''' join a users voice channel '''
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        # create a new VoiceEntry or move the existing one
        if s_id in self.clients:
            await self.clients[s_id].voice.move_to(voice_channel)
        else:
            voice_client = await self.bot.join_voice_channel(voice_channel)
            newEntry     = VoiceEntry(s_id, voice_client, msg.channel, self)
            self.clients[s_id] = newEntry
        
        # return text message
        return ON_VOICE_JOIN
    
    async def play(self, msg):
        ''' play a youtube audio if in voice channel '''
        try:
            # check for voice channel
            voice_channel = msg.author.voice_channel
            server        = msg.server
            if server is None: return ON_NO_SERVER
            if voice_channel is None: return ON_NO_VOICE
            s_id  = server.id
            
            # get youtube link
            song = ' '.join(str(msg.content).split()[1:])
            if not song.startswith("http"):
                song = await self.kbot.youtube.getSearchUrl(song)
            
            # play song
            if s_id in self.clients:
                info  = await self.kbot.youtube.getMetaData(song)
                title = info['title'] 
                
                voiceEntry = self.clients[s_id]
                voiceEntry.queue.append({"url":song, "title":title})
                voiceEntry.channel = msg.channel
                
                if not voiceEntry.isPlaying:
                    voiceEntry.get_next_song()
                    return None
                else:
                    message = ON_SONG_ADD.format(title)
                    return message
            else:
                return ON_NO_ENTRY
            
        except Exception as e:
            print("Error in play: " + str(e))
        
    async def pause(self, msg):
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        if s_id in self.clients:
            self.clients[s_id].pause()
            return None
        else:
            return ON_NO_ENTRY
        
    async def resume(self, msg):
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        if s_id in self.clients:
            self.clients[s_id].resume()
            return None
        else:
            return ON_NO_ENTRY
        
    async def skip(self, msg):
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        if s_id in self.clients:
            self.clients[s_id].skip()
            return None
        else:
            return ON_NO_ENTRY
        
    async def volume(self, msg):
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        if s_id in self.clients:
            try:
                volume = int(str(msg.content).split()[1])
                self.clients[s_id].setVolume(volume)
                return None
            except:
                return ON_BAD_VOLUME
        else:
            return ON_NO_ENTRY
        
    async def queue(self, msg):
        # check for voice channel
        voice_channel = msg.author.voice_channel
        server        = msg.server
        if server is None: return ON_NO_SERVER
        if voice_channel is None: return ON_NO_VOICE
        s_id  = server.id
        
        if s_id in self.clients:
            songs   = self.clients[s_id].queue
            current = self.clients[s_id].currentSong
            message = u"Playing : **" + repr(current) + "**\n"
            for pos, song in enumerate(songs):
                message += u"{0}. **{1}**\n".format(pos + 1, song["title"])
            return message
        else:
            return ON_NO_ENTRY











