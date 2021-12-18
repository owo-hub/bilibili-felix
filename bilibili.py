import discord
from discord.ext import tasks, commands
from discord.utils import get
from datetime import datetime
import urllib.parse, re
from urllib.request import urlopen
import json
import os
import io
import asyncio
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()

try:
    BOT_TOKEN = os.environ['DISCORD_TOKEN']
except:
    BOT_TOKEN = read_token()
    
client = commands.Bot(command_prefix='b?', intents=discord.Intents.all())
client.remove_command('help')

last_bilibili_status = True

@tasks.loop(minutes=1)
async def bilibili_notifs_loop():
    global last_bilibili_status
    global update_channel
    global status_role
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
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-gpu')
        chrome_options.add_argument('no-sandbox')
        chrome_options.add_argument('window-size=1280,720')
        try:
            chrome_options.binary_location = os.environ['GOOGLE_CHROME_BIN']
            chromedriver = os.environ['CHROMEDRIVER_PATH']
        except:
            chromedriver = f"{os.getcwd()}\\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver, options=chrome_options)
        driver.get(url=live_url)
        await asyncio.sleep(2)
        rank = driver.find_element(By.XPATH, '//*[@id="head-info-vm"]/div/div/div[2]/div[1]/a[3]/div/span').text
        rank = rank.replace("No. ", "")
        gifts = driver.find_element(By.XPATH, '//*[@id="head-info-vm"]/div/div/div[2]/div[1]/div[2]/span').text
        gifts = gifts.replace(" 万", "")
        image = driver.get_screenshot_as_png()
        driver.quit()
        
        buffer = io.BytesIO(image)
        cropped = Image.open(buffer)
        area = (30, 164, 936, 674)
        cropped = cropped.crop(area)
        buffer = io.BytesIO()
        cropped.save(buffer, format="PNG")
        buffer.seek(0)
        """
        
        embed = discord.Embed()
        embed.colour = 0x01A1D6
        embed.set_author(name=f"{streamer_name}님이 방송을 시작했습니다.", url=live_url, icon_url=avatar_url)
        embed.title = f"{emojis['live1']}{emojis['live2']} {title}"
        embed.add_field(name=f"{emojis['followers']} **팔로워**", value=f"```\n{follower}명```", inline=True)
        try:
            embed.add_field(name=f"{emojis['pointer']} **포인트**", value=f"```\n{gifts}만 개```", inline=True)
            embed.add_field(name=f"{emojis['rank']} **순위**", value=f"```\n{rank}위```", inline=True)
        except:
            embed.add_field(name=f"{emojis['online']} **인기도**", value=f"```\n{online}명```", inline=True)
        embed.description = f"[{emojis['bilibili']} 방송 보러 가기]({live_url})"

        logo_url = "https://logodix.com/logo/1224389.png"
        logotext_url = "https://i0.hdslb.com/bfs/archive/9e5f278027ae7f1e1933b6e4002870361da6c20b.png"
        #embed.set_image(url=f"attachment://bilibili-{mid}-screenshot.png")
        embed.set_image(url=cover_url)
        embed.set_thumbnail(url=logotext_url)
        embed.set_footer(icon_url=logo_url, text=live_url)
        #embed.timestamp = datetime.now()

        #await update_channel.send(content="@everyone", file=discord.File(buffer, f"bilibili-{mid}-screenshot.png"), embed=embed)
        await update_channel.send(content="@everyone", embed=embed)
        
        await client.get_guild(656862634754310174).get_member(client.user.id).edit(nick=f"📺 {title}")
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
               name=f"💙 비리비리에서",
               url="https://www.twitch.tv/felix_overwatch"
           )
       )
        #await update_channel.send(content="@everyone", embed=embed)

    elif live_status == 0 and last_bilibili_status == True: # 방송 종료
        last_bilibili_status = False

        embed = discord.Embed()
        embed.colour = discord.Color.red()
        embed.set_author(name=f"{streamer_name}님이 방송을 종료했습니다.", url=live_url, icon_url=avatar_url)
        embed.title = f"{emojis['nolive1']}{emojis['nolive2']} {title}"
        embed.add_field(name=f"{emojis['followers']} **팔로워**", value=f"```\n{follower}명```", inline=True)
        embed.add_field(name=f"{emojis['online']} **인기도**", value=f"```\n{online}명```", inline=True)

        embed.description = f"[{emojis['bilibili']} 팔로우 하러 가기]({live_url})"

        logo_url = "https://logodix.com/logo/1224389.png"
        logotext_url = "https://i0.hdslb.com/bfs/archive/9e5f278027ae7f1e1933b6e4002870361da6c20b.png"
        #embed.set_image(url=cover_url)
        embed.set_thumbnail(url=logotext_url)
        embed.set_footer(icon_url=logo_url, text=live_url)
        #embed.timestamp = datetime.now()

        await update_channel.send(embed=embed)
        await client.get_guild(656862634754310174).get_member(client.user.id).edit(nick="")
        await status_role.edit(name="❌ 비리비리 방송 중 아님")
        await client.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(
                name="😏 무언가"
            )
        )
        
    if last_bilibili_status == True:
        await status_role.edit(name=f"📈인기도 {online} ❤️팔로워 {follower}명")

@client.event
async def on_ready():
    global last_bilibili_status
    global update_channel
    global status_role
    global emojis
    global log_channel
    update_channel = client.get_channel(885140926157176882)
    print("Loaded Notification Channel.")
    status_role = client.get_guild(656862634754310174).get_role(868276590843408385)
    print("Loaded Status Role.")
    log_channel = client.get_channel(884985900361187379)
    print("Loaded Log Channel.")
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
    await log_channel.send("Bot is ready")
    bilibili_notifs_loop.start()
    
client.run(BOT_TOKEN)
