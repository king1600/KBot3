'''
Created on Oct 13, 2016

@author: King
'''
import json
import asyncio
import aiohttp
import random
from urllib.parse import quote
from _cleverbot import Cleverbot

async def decision(probability):
        ''' generate probability '''
        return random.random() < (probability / 100.)

async def main():
    for x in range(30):
        print(await decision(20))
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())