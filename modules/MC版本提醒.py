import json

import requests
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from modules.mysql import Sql

channel = Channel.current()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


@channel.use(SchedulerSchema(timers.every_custom_minutes(1)))
async def mcbv(app: Ariadne):
    version = []
    verlist = (await Sql.get_mcversion('version_list')).split("|")
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
            for g in (await Sql.get_mcversion('version_open_group')).split("|"):
                await app.send_group_message(int(g),
                                             MessageChain([Plain(f'你有新的Minecraft版本请注意查收：\n版本号：{v}')]))
            newver = "|".join(verlist)
            await Sql.change_mcversion('version_list', newver)
