import os
import sys
import subprocess
import discord
import aiohttp
import asyncio
import async_timeout
import time
import json
import momo_utils
import random
import math
import threading
import time
from pathlib import Path

bot = discord.Client()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
with open('mimi_data.json') as data_file:
    user_opts = json.load(data_file)

server_opts=user_opts['server_opt'][0]
api_key=server_opts['api_key']


from contextlib import suppress

async def doPost(session, url):
    with async_timeout.timeout(10):
        async with session.post(url) as response:
            return await response.text()


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

def get_standings(js):
    outstr = 'Standings for top momocoin:\n';
    for obj in js :
        outstr = '%s<@%s> with a balance of %f\n' % (outstr, obj['id'], obj['balance']);
    return outstr;

@bot.event
async def on_message(message):
    server = bot.get_server(server_opts['serverid'])
    channel = bot.get_channel(server_opts['channelid'])
    args = message.content.lower()
    if message.author == bot.user:
        return
    elif args.startswith('!standings'):
        out = 'failed'
        with async_timeout.timeout(10):
          async with aiohttp.ClientSession() as session:
            out = await fetch(session, 'http://localhost:8000/wallet/discord/standings/5')
        try:
          js = json.loads(out)
          outstr = get_standings(js);
          await bot.send_message(message.channel, '%s' % (outstr));
        except Exception as inst:
          await bot.send_message(message.channel, 'Failure occurred %s' % inst);
    elif args.startswith('!balance'):
        out = 'failed'
        with async_timeout.timeout(10):
          async with aiohttp.ClientSession() as session:
            out = await fetch(session, 'http://localhost:8000/wallet/discord/%s' % message.author.id)
        try:
          js = json.loads(out)
          await bot.send_message(message.channel, 'Hello %s, your balance is: %s' % (message.author, js['balance']));
        except Exception as inst:
          await bot.send_message(message.channel, 'Failure occurred %s' % inst);
    elif args.startswith('!tip'):
        extra = ''
        try:
          tokens = args.split()
          delta = float(tokens[2])
          userid = tokens[1][2:-1]
          if userid[0] == '!':
            userid = userid[1:]
          url = 'http://localhost:8000/wallet/discord/tip/%s/%s/%s?api_key=%s' % (message.author.id, userid, tokens[2], api_key)
          out = 'failed'
          with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
              out = await doPost(session, url)
            extra = '%s' % out
            js = json.loads(out)
            await bot.send_message(message.channel, 'Tip completed. Your new balance is %s, %s' % (js['balance'], message.author));
        except Exception as inst:
          final_message = inst
          if (extra != ''):
            final_message = extra
          await bot.send_message(message.channel, 'Failure occurred: %s' % (final_message));
    elif args.startswith('!claim'):
        extra = ''
        try:
            url = 'http://localhost:8000/wallet/discord/claimcoin/%s' % (message.author.id)
            out = 'failed'
            with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    out = await doPost(session, url)
                    extra = '%s' % out
                    js = json.loads(out)
                    delta = int(js['delta'])
                    if (delta > 1):
                        await bot.send_message(message.channel, 'Wow! %s coins claimed. Your new balance is %s, %s' % (js['delta'], js['balance'], message.author));
                    elif (delta < 1):
                        await bot.send_message(message.channel, 'Unlucky, %s of a coin claimed. Your new balance is %s, %s' % (js['delta'], js['balance'], message.author));
                    else:
                        await bot.send_message(message.channel, 'Daily coin claimed. Your new balance is %s, %s' % (js['balance'], message.author));
        except Exception as inst:
          final_message = inst
          if (extra != ''):
            final_message = extra
          await bot.send_message(message.channel, 'Failure occurred: %s' % (final_message));
    elif args.startswith('!gamble'):
        extra = ''
        try:
            tokens = args.split()
            bet = float(tokens[1])
            p = 0.5
            if (len(tokens) > 2):
                p = float(tokens[2])
            payout = bet / p - bet
            url = 'http://localhost:8000/wallet/discord/gamble/%s/%s/%s' % (message.author.id, bet, p)
            out = 'Failure occurred'
            with async_timeout.timeout(10):
              async with aiohttp.ClientSession() as session:
                out = await doPost(session, url)
              extra = '%s' % out
              js = json.loads(out)
              win = js['win']
              balance = js['balance']
              await bot.send_message(message.channel, 'Initiating bet with %s momocoins, success probability %s, and potential payout of %s!!' % (bet, p, payout));
              await asyncio.sleep(1)
              if (win == 'win'):
                  await bot.send_message(message.channel, 'Congratulations! You won %s momocoin, your new balance is %s, %s' % (payout, balance, message.author));
              else:
                  await bot.send_message(message.channel, 'Sorry %s, you lost your bet of %s! Your new balance is %s.' % (message.author, bet, balance));
        except Exception as inst:
          final_message = inst
          if (extra != ''):
              final_message = extra
          await bot.send_message(message.channel, 'Failure occurred: %s' % (final_message));


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('On these servers:')
    for server in bot.servers:
        print(server)
    print('--------------')
    await bot.change_presence(game=discord.Game(name='Cat goes fishing'))


#Run the server with the token
bot.run(server_opts['token'])

