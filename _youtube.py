#!/usr/bin/env python3
#! python3

'''
Created on Oct 12, 2016
@author:     King1600
@summary:    Youtube info fetcher
'''

import pafy
import json
import constants

from urllib.parse import quote
from bs4 import BeautifulSoup

class YoutubeExtractor(object):
    FORMAT = "m4a"
    
    def __init__(self, bot):
        self.bot     = bot
        self.session = self.bot.session

    def getVideoId(self, url):
        ''' Converts youtube url to video id only '''
        if 'youtu' in url:
            url = url.split("watch?v=")[-1]
        if '&' in url:
            url = url.split("&")[0]
        return url
    
    async def getVideoStream(self, url, fmt):
        ''' get video stream url from video '''
        url = self.getVideoId(url)
        stream = pafy.new(url, basic=False, gdata=False)
        return stream.getbest(preftype=fmt).url_https
    
    async def getAudioStream(self, url, fmt):
        ''' get audio stream url from video '''
        url = self.getVideoId(url)
        stream = pafy.new(url, basic=False, gdata=False)
        return stream.getbestaudio(preftype=fmt).url_https
    
    async def getThumbnail(self, url):
        ''' returns thumbnail url '''
        url = self.getVideoId(url)
    
        # decide which thumbnail to use if error
        thumb = constants.MAX_THUMBNAIL.format(id=url)
        try:
            async with self.session.get(thumb) as response:
                if str(response.status)[0] != '2': # error
                    raise Exception()
        except:
            thumb = constants.MIN_THUMBNAIL.format(id=url)
        return thumb
    
    async def getMetaData(self, url):
        ''' fetch video info from youtube.com/oembed '''
        link = self.getVideoId(url)
        link = constants.YOUTUBE_LINK.format(id=link)
        link = constants.YOUTUBE_OEMBED.format(url=link)
    
        async with self.session.get(link) as response:
            info = await response.text()
            return json.loads(info) # return json object
    
    async def getSearchUrl(self, query):
        ''' get the first result from youtube search '''
        requestUrl = quote(query)
        requestUrl = constants.YOUTUBE_SEARCH.format(
                        query = requestUrl)
        
        # start parsing data
        async with self.session.get(requestUrl) as response:
            data = await response.text()
            soup = BeautifulSoup(str(data), 'html.parser')
            divs = [d for d in soup.find_all('div')]
            divs = [d for d in divs if d.has_attr('class')]
            divs = [d for d in divs if 'yt-lockup-dismissable' in d['class']]
            
            # iterate throught results and return first one
            for d in divs:
                dt   = 'data-thumb'
                img  = d.find_all('img')[0]
                data = img['src'] if not img.has_attr(dt) else img[dt]
    
                # return full watch url
                videoId     = data.split('/')[-2]
                videoResult = constants.YOUTUBE_LINK.format(id=videoId)
                return videoResult
    
    async def argParse(self, kargs):
        # get url
        if 'url' in kargs:
            url = self.getVideoId(kargs['url'])
        elif 'search' in kargs:
            url = await self.getSearchUrl(kargs['search'])
        else:
            return 'Where de URL at doe ?.?'
    
        # final results string
        results = ""
    
        # get data
        for pos, mode in enumerate(kargs['modes']):
            out = ""
    
            # Get Video direct audio link
            if mode == 'audio':
                # correct the format if in args
                if 'format' in kargs:
                    if kargs['format'].lower() in ['m4a','webm']:
                        fmt = kargs['format'].lower()
                    else: fmt = 'm4a'
                else: fmt = 'm4a'
    
                # try getting stream link 
                try:
                    d_url = await self.getAudioStream(url, fmt)
                    try:
                        if 'raw' in kargs or 'direct' in kargs:
                            out += "Direct Audio link: " + d_url
                        else:
                            d_url = await self.bot.shortener.shortenUrl(d_url)
                            out += "Direct Audio link: " + d_url
                    except:
                        out += "Direct Audio link: " + d_url
    
                # handle stream error
                except Exception as e:
                    out += "[x] Failed to get audio link! "
                    out += str(e)
                 
            # Get Video Direct download link
            elif mode == 'video':
                # correct the format if in args
                if 'format' in kargs:
                    if kargs['format'].lower() in ['mp4','webm','flv']:
                        fmt = kargs['format'].lower()
                    else: fmt = 'mp4'
                else: fmt = 'mp4'
    
                # attempt to get stream url
                try:
                    d_url = await self.getVideoStream(url, fmt)
                    try:
                        if 'raw' in kargs or 'direct' in kargs:
                            out += "Direct Video link: " + d_url
                        else:
                            d_url = await self.bot.shortener.shortenUrl(d_url)
                            out += "Direct Video link: " + d_url
                    except:
                        out += "Direct Video link: " + d_url
    
                # handle error exception
                except Exception as e:
                    out += "[x] Failed to get video link! "
                    out += str(e)
    
            # Get Video title
            elif mode == 'title':
                try:
                    title = await self.getMetaData(url)
                    out += "Title: " + title['title']
                except Exception as e:
                    out += "[x] Failed to get title! "
                    out += str(e)
    
            # Get Video image link
            elif mode in ['thumb','thumbnail','image']:
                try:
                    thumb = await self.getThumbnail(url)
                    out += "Thumbnail Direct link: " + thumb
                except Exception as e:
                    out += "[x] Failed to get thumbnail url! "
                    out += str(e)
    
            # Get Video info
            elif mode in ['info','oembed','json','data']:
                try:
                    data = await self.getMetaData(url)
                    out += "Video info:\n```json\n"
                    out += json.dumps(data, indent=4, sort_keys=True)
                    out += "\n```"
                except Exception as e:
                    out += "[x] Couldn't retrieve json info: "
                    out += str(e)
    
            # Debug kargs
            elif mode == 'debug':
                out += "Command Arguments:\n```json\n"
                out += json.dumps(kargs, indent=4, sort_keys=True)
                out += "\n```"
    
            # Nothing
            else:
                pass
    
            # append outputs
            if out != '' and not out.isspace():
                if pos != 0: results += '\n' + out
                else: results += out
    
        # return final results string
        return results
    
