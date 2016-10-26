#!/usr/bin/env python3
#! python3
# -*- coding: utf-8 -*-

'''
Created on Oct 13, 2016
@author:     King1600
@summary:    Urban Dictionary define stripped from pypi urbandict
'''

from bs4 import BeautifulSoup
from urllib.parse import quote
from html.parser import HTMLParser
from constants import URBAN_DICT, INSULT_LINK

class TermType(object): pass
class DictUrlError(Exception): pass
class TermTypeRandom(TermType): pass

class UrbanDictParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self._section = None
        self.translations = []

    def handle_starttag(self, tag, attrs):
        if tag != "div": return

        attrs_dict = dict(attrs)
        div_class = attrs_dict.get('class')
        if div_class in ('def-header', 'meaning', 'example'):
            self._section = div_class

            # NOTE: assume 'word' is the first section
            if div_class == 'def-header':
                self.translations.append(
                    {'word': '', 'def': '', 'example': ''})

    def handle_endtag(self, tag):
        if tag == 'div':
            #NOTE: assume there is no nested <div> in the known sections
            self._section = None

    def handle_data(self, data):
        if not self._section: return

        if self._section == 'meaning':
            self._section = 'def'
        elif self._section == 'def-header':
            data = data.strip()
            self._section = 'word'

        self.translations[-1][self._section] += normalize_newlines(data)

def normalize_newlines(text):
    return text.replace('\r\n','\n').replace('\r','\n')

async def pruneChars(word):
    badChars = list("\r\n\t\b")
    while True:
        removeFront, removeBack = False, False
        for c in badChars:
            if word.startswith(c): removeFront = True
            if word.endswith(c): removeBack = True
        if removeFront: word = word[1:]
        if removeBack: word = word[:-1]
        if not removeFront and not removeBack: break
    return word

######################################

class UrbanDictionary(object):
    ''' urban dictionary lookup '''
    
    def __init__(self, session):
        self.session = session
        
    async def define(self, query):
        ''' get urban dictionary first definition '''
        url = URBAN_DICT + quote(query)
        
        # perform http request
        async with self.session.get(url) as resp:
            # get definition
            data   = await resp.text()
            parser = UrbanDictParser()
            parser.feed(data)
            info   = parser.translations[0]
            #_word  = await pruneChars(info['word'])
            _def   = await pruneChars(info['def'])
            return _def
            
    async def generateInsult(self):
        ''' generate insult '''
        async with self.session.get(INSULT_LINK) as resp:
            data = await resp.text()
            soup = BeautifulSoup(data, 'html.parser')
            divs = [d for d in soup.find_all('div')]
            divs = [d for d in divs if d.has_attr('class')]
            insult = divs[1].text
            return await pruneChars(insult)