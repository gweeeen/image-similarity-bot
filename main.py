import discord
from discord.ext import commands
intents = discord.Intents()

#MEMBERS AND MESSAGES PRIVILEGED INTENTS are required
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

#change this if you want more/less stricter detections
#lower = stricter
#higher = less stricter
#based on internal testing, around 0.85-0.95 works best
threshold = 0.95

@bot.event
async def on_ready():
    return print('ready for action')

def check_pfp(user):
    import cv2
    import os
    import image_similarity_measures
    from sys import argv
    from image_similarity_measures.quality_metrics import rmse, ssim, sre
    from PIL import Image
    import urllib.request
    import urllib
    import requests
    import io

    if user.avatar==None:
        return 0

    is_smaller = False

    test_img = cv2.imread('scammer.png')
    width = test_img.shape[1]

    response = requests.get(user.avatar.url)
    if response.status_code==429:
        raise RuntimeError('stinky ratelimit')
    with open(f'{user.id}.png', 'wb') as f:
        f.write(response.content)
        f.close()

    ssim_measures = {}
    rmse_measures = {}
    sre_measures = {}
    
    data_img = cv2.imread(f'{user.id}.png')
    width1 = data_img.shape[1]
    if width1 > width:
        image = Image.open(f'{user.id}.png')
        newimg = image.resize((width,width))
        newimg.save(f'{user.id}.png')
    elif width1 < width:
        is_smaller = True
        image = Image.open('scammer.png')
        newimg = image.resize((width,width))
        newimg.save(f'{user.id}_1.png')
    if is_smaller:
        test_img = cv2.imread(f'{user.id}_1.png')
    data_img = cv2.imread(f'{user.id}.png')
    ssim_measures= ssim(test_img, data_img)
    return ssim_measures

@bot.event
async def on_message(message):
    if message.content.startswith('!test'):
        user = message.content.replace('!test ','',1)
        user = message.guild.get_member(int(user))
        await message.channel.send('testing...')
        result = await self.bot.loop.run_in_executor(None, lambda: check_pfp(user))
        if result > threshold:
            await message.channel.send(f'{result} (**WARNING: UNSAFE**, threshold is {threshold})')
        else:
            await message.channel.send(f'{result} (safe, threshold is {threshold})')
    elif message.content.startswith('!fulltest'):
        await message.channel.send('this could take a while, give it a bit...')
        sus = []
        scanned = []
        try:
            alreadyscanned = message.attachments[0]
            import requests
            if not alreadyscanned.url.endswith('.txt'):
                raise ValueError('not txt')
            response = requests.get(alreadyscanned.url)
            import ast
            scanned = ast.literal_eval(response.text)
            print('copied already scanned users!')
        except:
            print('copy failed/no attachment, skipping...')
        for user in message.guild.members:
            if user.id in scanned:
                continue
            scanned.append(user.id)
            try:
                result = await self.bot.loop.run_in_executor(None, lambda: check_pfp(user))
            except:
                x = open('scanned.txt','w+',encoding='utf-8')
                x.write(f'{scanned}')
                x.close()
                await message.channel.send('error occurred or ratelimited, giving up.\njust send the txt file the bot sends in this message when running !fulltest again to exclude already scanned ids\n**a second file with the suspicious ids will be sent**',file=discord.File(fp='scanned.txt'))
                break
            if result > threshold:
                sus.append(user.id)
        x = open('sus.txt','w+',encoding='utf-8')
        x.write(f'{sus}')
        x.close()
        x = open('scanned.txt','w+',encoding='utf-8')
        x.write(f'{scanned}')
        x.close()
        await message.channel.send(file=discord.File(fp='sus.txt'))

bot.run('token')
