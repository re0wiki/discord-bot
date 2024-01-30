import requests
import uuid
import discord
import io

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

guild_id = "779185920670171136"

def get_image_content_from_url(url):
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return -1
        
    return discord.File(io.BytesIO(r.content), f'{uuid.uuid4()}.{url.split(".")[-1]}')

def get_dynamic(id):
    r = requests.get(f'https://api.bilibili.com/x/polymer/web-dynamic/v1/detail?id={id}', headers=headers)
    if r.status_code != 200:
        return -1
    
    res = r.json()["data"]["item"]["modules"]

    avatar = res["module_author"]["face"]
    pub_time = res["module_author"]["pub_time"]
    username = res["module_author"]["name"]
    content = res["module_dynamic"]["desc"]["text"]
    pics = res["module_dynamic"]["major"]["draw"]["items"]

    return {"avatar": avatar, "username": username, "pub_time": pub_time, "content": content, "pics": pics}

# discord
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or str(message.guild.id) != guild_id:
        return
    
    if message.content.find("opus/") != -1:
        dynamic_id = message.content.split("opus/")[1].split("?")[0]
    elif message.content.find("t.bilibili.com/") != -1:
        dynamic_id = message.content.split("t.bilibili.com/")[1].split("?")[0]
    else:
        return
    
    dynamic = get_dynamic(dynamic_id)
    if dynamic == -1:
        await message.channel.send("获取动态失败")
        return
        
    files = []
    need_stop = False
    for pic in dynamic["pics"]:
        content = get_image_content_from_url(pic["src"])
        if content == -1:
            await message.channel.send("获取动态图片失败")
            need_stop = True
            break
        files.append(content)

    if need_stop:
        return
        
    text = f'{dynamic["content"]}\n发布时间: {dynamic["pub_time"]}'

    webhook = await message.channel.create_webhook(name="BilibiliDynamicRewrite")
    await webhook.send(content=text, files=files, avatar_url=dynamic["avatar"], username=dynamic["username"])
    await webhook.delete()
        

client.run("") # discord bot token
