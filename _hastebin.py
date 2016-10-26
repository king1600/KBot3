#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-

'''
Created on Oct 19, 2016
@author:     King1600
@summary:    HastebinApi
'''

from constants import HASTEBIN, HASTEBIN_POST

class Hastebin(object):
    ''' Generate Hastebin Posts '''

    def __init__(self, session):
        self.session = session
        
    async def generate(self, text):
        data = text.encode('utf-8')
        
        async with self.session.post(HASTEBIN_POST, data=data) as resp:
            info = await resp.json()
            return HASTEBIN + "/" + info['key']
        