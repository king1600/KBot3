#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-\

'''
Created on Oct 12, 2016
@author:     King1600
@summary:    All KBot Constants
'''

import sys
import multiprocessing

### VARIABLES ###
CHAR_LIMIT      = 500
DELETE_LIMIT    = 500
RESPOND_CHANCE  = 20
ARGS_SPLIT      = "|"
HTTP_THREADS    = int(multiprocessing.cpu_count())
HTTP_BUFFER     = 1024
PLAYER_VOLUME   = 0.5

### File Paths ###
BOT_PATH        = "bot.info"
CONF_PATH       = "config.json"
COMMANDS_PATH   = "commands.info"
LOG_PATH        = "bot.log"
FFMPEG          = "ffmpeg"

### ARRAYS ###
ONS   = ['enable','on','1','activate','active']
OFFS  = ['disable','off','0','deactivate','deactive']
YOUTUBE_MODES = ['audio','video','title','thumb','thumbnail','image','info','embed','json','data','debug']

### LINKS ###
JOIN_LINK       = "https://discordapp.com/oauth2/authorize?client_id={id}&scope=bot&permissions=8"
GOOGLE_SHORT    = "https://content.googleapis.com/urlshortener/v1/url?key={key}&alt=json"
INSULT_LINK     = "http://www.insultgenerator.org/"
YOUTUBE_OEMBED  = "https://www.youtube.com/oembed?url={url}"
YOUTUBE_SEARCH  = "https://youtube.com/results?search_query={query}"
YOUTUBE_LINK    = "https://www.youtube.com/watch?v={id}"
YOUTUBE_GDATA   = "https://www.googleapis.com/youtube/v3/videos?id={id}&key={key}&part=contentDetails"
MAX_THUMBNAIL   = "http://img.youtube.com/vi/{id}/maxresdefault.jpg"
MIN_THUMBNAIL   = "http://img.youtube.com/vi/{id}/hqdefault.jpg"
URBAN_DICT      = "http://www.urbandictionary.com/define.php?term="
HASTEBIN        = "http://hastebin.com"
HASTEBIN_POST   = "http://hastebin.com/documents"
