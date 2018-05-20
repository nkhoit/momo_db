import os
import sys
import subprocess
import discord
import aiohttp
import asyncio
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
with open('user_data.json') as data_file:
    user_opts = json.load(data_file)

server_opts=user_opts['server_opt'][0]
serv_base_url=server_opts['base_url']
pics_dir=server_opts['pics_dir']
mimi_dir=server_opts['mimi_dir']
mimo_dir=server_opts['mimo_dir']
other = {}


from contextlib import suppress


@bot.event
async def on_message(message):
    server = bot.get_server(server_opts['serverid'])
    channel = bot.get_channel(server_opts['channelid'])
    args = message.content.lower()
    #if message.author == bot.user:
    #    return
    if args.startswith('!setchannel'):
        other['home'] = message.channel
        await bot.send_message(message.channel, 'Meow, now lurking');
    elif args.startswith('!momo'):
        url = momo_utils.get_random_url(pics_dir, serv_base_url)
        await bot.send_message(message.channel, url)
    elif args.startswith('!mimo'):
        url = momo_utils.get_random_url(mimo_dir, server_opts['mimo_base'])
        await bot.send_message(message.channel, url)
    elif args.startswith('!mimi'):
        url = momo_utils.get_random_url(mimi_dir, server_opts['mimi_base'])
        await bot.send_message(message.channel, url) 
    elif args.startswith('!bruce'):
        url = 'http://www.momobot.net/cat/bruce1.jpg';
        await bot.send_message(message.channel, url)
    elif args.startswith('!hairycrab'):
        await bot.send_message(message.channel, 'https://giant.gfycat.com/EqualDemandingAiredale.webm')
    elif args.startswith('!meow'):
        await bot.send_message(message.channel, 'Mrrrowl')
    elif args.startswith('!hoppes') or args.startswith('!thankmew'):
        await bot.send_message(message.channel, 'https://yt3.ggpht.com/-P7lfEaDGB6M/AAAAAAAAAAI/AAAAAAAAAAA/qZZA1cFajM4/s900-c-k-no-mo-rj-c0xffffff/photo.jpg')
    elif args.startswith('!brickle') or args.startswith('!iulius'):
        rand = random.randint(0,3)
        if rand > 2:
          await bot.send_message(message.channel, 'https://www.youtube.com/watch?v=992xtvLAfKo');
        if rand > 1:
          await bot.send_message(message.channel, 'https://www.youtube.com/watch?v=mxzgwJ8tSE0');
        elif rand > 0:
          await bot.send_message(message.channel, 'https://www.youtube.com/watch?v=yO7MWuJ7zLA');
        else:
          await bot.send_message(message.channel, 'https://www.youtube.com/watch?v=IIKPA8Z-D0g');
        #if rand > 0:
        #    await bot.send_message(message.channel, 'https://giphy.com/gifs/gifnews-dinosaurs-nEUMeGI3r3YAw')
        #else:
        #    await bot.send_message(message.channel, 'http://media.giphy.com/media/Zg7clvqHE3CdW/giphy.gif')
    elif args.startswith('!haywood'):
        await bot.send_message(message.channel, 'https://giphy.com/gifs/coding-srbiWWa0VW2YM')
    elif args.startswith('!goodgirl'):
        url = momo_utils.get_random_url(mimi_dir, server_opts['mimi_base'])
        i = random.randint(10,12)
        f = math.floor(math.fabs(random.gauss(0,1)))
        tot = i + f
        await bot.send_message(message.channel, 'This Mimi is a good girl, rated %s/10: %s' % (i, url))
    elif args.startswith('!goodboy'):
        url = momo_utils.get_random_url(pics_dir, serv_base_url)
        i = random.randint(10,12)
        f = math.floor(math.fabs(random.gauss(0,1)))
        tot = i + f
        await bot.send_message(message.channel, 'This momo is a good boy, rated %s/10: %s' % (i, url))
    elif args.startswith('!badboy'):
        bad_boys = ['TP1', 'TP2', 'TP3']
        choice = random.sample(bad_boys, 1)[0]
        url = 'http://momobot.net/cat/%s.jpg' % choice
        await bot.send_message(message.channel, 'Bad to the bone %s' % url)
    elif args.startswith('!panic'):
        url = 'https://i.redd.it/74kak5q92zsy.jpg'
        await bot.send_message(message.channel, '%s' % url)
    elif args.startswith('!pfeonix'):
        i = random.randint(0,5)
        url = ''
        if i > 4:
            url = 'https://www.twitch.tv/videos/158990970'
        else:
            url = 'https://giphy.com/gifs/dreams-sloth-dreaming-dQCmKY4IgywFy'
        await bot.send_message(message.channel, '%s' % url)
    elif args.startswith('!splaytree'):
        url = 'https://giphy.com/gifs/sloth-look-at-all-the-fucks-i-give-jsnACY5sBbPDa'
        await bot.send_message(message.channel, '%s' % url)
    elif args.startswith('!saltytrump'):
        url = 'https://giphy.com/gifs/sloth-hard-partying-HetW1AVRvG1fq'
        await bot.send_message(message.channel, '%s' % url)
    elif args.startswith('!mmomo'):
        await bot.send_message(message.channel, '$mmomo')
    elif args.startswith('!isatest'):
        await bot.send_message(other['home'], 'Test complete! MROWL!');
    elif args.startswith('!now'):
        await bot.send_message(message.channel, '%s' % int(time.time()));
    else:
        #Check if "khadgar" is somewhere in the text
        text = message.content.lower().split(' ')
        if "khadgar" in text:
            await bot.send_message(message.channel, 'I think you mean Dadgar')
    
async def checkfs():
    messagePath = Path('/home/ubuntu/message')
    if (messagePath.exists()):
      with open('/home/ubuntu/message', 'r') as f:
        var = f.read().replace('\n','')
        await bot.send_message(other['home'], var)
      os.remove('/home/ubuntu/message')

async def loopcheckfs():
    while True:
      await checkfs()
      await asyncio.sleep(1)

def startStuff():
  print('blah, starting stuff')
  loop = asyncio.new_event_loop()
  try:
    loop.run_until_complete(loopcheckfs())
  except Exception as e:
    pass #todo log error

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('On these servers:')
    for server in bot.servers:
        print(server)
    print('--------------')
#    checkfs()
    #t = threading.Thread(target=startStuff)
    #t.start()
    await bot.change_presence(game=discord.Game(name='Cat goes fishing'))


#Run the server with the token
bot.loop.create_task(loopcheckfs())
bot.run(server_opts['token'])

