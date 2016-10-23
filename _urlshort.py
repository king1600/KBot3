#!/usr/bin/env python3
#! python3

'''
Created on Oct 22, 2016
@author:     King1600
@summary:    Goo.gl url shortener
'''

import json
import asyncio
from constants import *

class UrlShortener(object):
    ''' use google api to shorten link '''
    
    def __init__(self, bot):
        self.bot     = bot
        self.session = self.bot.session
        self.apiKey  = self.bot.googleKey
        
    async def shortenUrl(self, url):
        query   = GOOGLE_SHORT.format(key=self.apiKey)
        payload = json.dumps({"longUrl": url})
        hdr     = {'content-type': 'application/json'}
        
        async with self.session.post(query, data=payload, headers=hdr) as resp:
            if str(resp.status)[0] != '2':
                raise Exception("URL Error: " + str(resp.reason))
            data = await resp.text()
            data = json.loads(data)
            return data['id']