import discord
from discord.ext import tasks, commands
from discord.utils import get
import configparser
from datetime import datetime
import urllib.parse, re
from urllib.request import urlopen
import json

BOT_TOKEN = os.environ['TOKEN']
client = commands.Bot(command_prefix='b?', intents=discord.Intents.all())
client.remove_command('help')

last_bilibili_status = False

@tasks.loop(minutes=1)
async def bilibili_notifs_loop():
    global last_bilibili_status
    global update_channel
    global emojis
    
    mid = "1109994528"
    data = json.loads(urlopen(f'https://api.bilibili.com/x/space/acc/info?mid={mid}&jsonp=jsonp').read().decode('utf-8')).get('data')
    follower = format(json.loads(urlopen(f'https://api.bilibili.com/x/relation/stat?vmid={mid}&jsonp=jsonp').read().decode('utf-8'))['data']['follower'], ",")
    streamer_name = data['name']
    live_status = data['live_room']['liveStatus']
    live_url = data['live_room']['url']
    avatar_url = data['face']
    online = format(data['live_room']['online'], ",")
    level = data['level']
    title = data['live_room']['title']
    cover_url = data['live_room']['cover']
    
    if live_status == 1 and last_bilibili_status == False: # 방송 시작
        last_bilibili_status = True

        embed = discord.Embed()
        embed.colour = 0x01A1D6
        embed.set_author(name=f"{streamer_name}님이 방송을 시작했습니다.", url=live_url, icon_url=avatar_url)
        embed.title = f"{emojis['live1']}{emojis['live2']} {title}"
        embed.add_field(name=f"{emojis['followers']} **팔로워**", value=f"```\n{follower}명```", inline=True)
        #embed.add_field(name=f"{emojis['pointer']} **레벨**", value=f"```\n{data['pointer']}```", inline=True)
        embed.add_field(name=f"{emojis['online']} **온라인**", value=f"```\n{online}명```", inline=True)
        #embed.add_field(name=f"{emojis['rank']} **순위**", value=f"```\n{data['rank']}```", inline=True)
        embed.description = f"[{emojis['bilibili']} 방송 보러 가기]({live_url})"

        logo_url = "https://logodix.com/logo/1224389.png"
        logotext_url = "https://i0.hdslb.com/bfs/archive/9e5f278027ae7f1e1933b6e4002870361da6c20b.png"
        #embed.set_image(url=f"attachment://bilibili-{mid}-screenshot.png")
        #embed.set_image(url=cover_url)
        #embed.set_thumbnail(url=logotext_url)
        embed.set_footer(icon_url=logo_url, text=live_url)
        #embed.timestamp = datetime.now()

        await update_channel.send(embed=embed)

    elif live_status == 0 and last_bilibili_status == True: # 방송 종료
        last_bilibili_status = False

        embed = discord.Embed()
        embed.colour = discord.Color.red()
        embed.set_author(name=f"{streamer_name}님이 방송을 종료했습니다.", url=live_url, icon_url=avatar_url)
        embed.title = f"{emojis['nolive1']}{emojis['nolive2']} {title}"
        embed.add_field(name=f"{emojis['followers']} **팔로워**", value=f"```\n{follower}명```", inline=True)
        #embed.add_field(name=f"{emojis['pointer']} **레벨**", value=f"```\n{data['pointer']}```", inline=True)
        embed.add_field(name=f"{emojis['online']} **마지막 온라인**", value=f"```\n{online}명```", inline=True)
        #embed.add_field(name=f"{emojis['rank']} **순위**", value=f"```\n{data['rank']}```", inline=True)

        embed.description = f"[{emojis['bilibili']} 팔로우 하러 가기]({live_url})"

        logo_url = "https://logodix.com/logo/1224389.png"
        logotext_url = "https://i0.hdslb.com/bfs/archive/9e5f278027ae7f1e1933b6e4002870361da6c20b.png"
       # embed.set_image(url=cover_url)
        #embed.set_thumbnail(url=logotext_url)
        embed.set_footer(icon_url=logo_url, text=live_url)
        #embed.timestamp = datetime.now()

        await update_channel.send(embed=embed)

@client.event
async def on_ready():
    global update_channel
    global emojis
    update_channel = client.get_channel(885140926157176882)
    print("Loaded Notification Channel.")
    emojis = {
        'bilibili': client.get_emoji(885035459242229780),
        'live1': client.get_emoji(885040582395842570),
        'live2': client.get_emoji(885040582421004298),
        'nolive1': client.get_emoji(885040403873685524),
        'nolive2': client.get_emoji(885040410924290129),
        'pointer': client.get_emoji(885000363374161940),
        'rank': client.get_emoji(885000363097325610),
        'online': client.get_emoji(884999447107473439),
        'followers': client.get_emoji(885005729038233632)}
    print("Loaded Emojis")
    print("----------------------------------------")
    print("Bot is ready!")
    print(f"{client.user} ({client.user.id})")
    print("----------------------------------------")
    bilibili_notifs_loop.start()
    
client.run(BOT_TOKEN)
