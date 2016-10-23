#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-

'''
Created on Oct 19, 2016
@author:     King1600
@summary:    HastebinApi
'''

import json
import asyncio
from constants import HASTEBIN, HASTEBIN_POST

class Hastebin(object):
    ''' Generate Hastebin Posts '''
    
    headers = {
        'Content-Type':'application/json; charset=UTF-8'
    }

    def __init__(self, session):
        self.session = session
        
    async def generate(self, text):
        hdr = self.headers
        data = text.encode('utf-8')
        
        async with self.session.post(HASTEBIN_POST, data=data) as resp:
            info = await resp.json()
            return HASTEBIN + "/" + info['key']
        