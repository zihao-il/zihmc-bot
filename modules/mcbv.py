from graia.saya import Channel
import json
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

channel = Channel.current()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


def get_vtxt(path):
    with open(path, 'r', encoding='utf-8') as v:
        vv = v.read().split("\n")
    return vv


path = "data/mcbv.txt"

qqgroup = [933238308, 855150997, 562664290, 196619774]

@channel.use(SchedulerSchema(timers.every_custom_minutes(1)))
async def mcbv(app: Ariadne):
    version = []
    verlist = get_vtxt(path)
    try:
        mcr = requests.get("https://bugs.mojang.com/rest/api/2/project/10200/versions", headers=headers)
        mc_json = json.loads(mcr.text)
        for v in mc_json:
            if not v['archived'] and v['released']:
                version.append(v['description'])
    except:
        return
    for v in version:
        if v not in verlist:
            verlist.append(v)
            for g in qqgroup:
                await app.sendGroupMessage(g, MessageChain.create(f'你有新的Minecraft版本请注意查收：\n版本号：{v}'))
            with open(path, "a", encoding="utf-8") as a:
                a.write(v + "\n")
