import json

import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from modules.mysql import Sql

channel = Channel.current()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
sections = [{'name': 'fb_Beta',
             'url': 'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001185332/articles?per_page=5'},
            {'name': 'fb_Release',
             'url': 'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001186971/articles?per_page=5'}]


#
@channel.use(SchedulerSchema(timers.every_custom_minutes(1)))
async def fbbv(app: Ariadne):
    for sv in sections:
        try:
            mcfb = requests.get(sv["url"], headers=headers, timeout=5)
            mcfb_json = json.loads(mcfb.text)
        except:
            return
        fb_name = mcfb_json["articles"][0]["name"]
        if await Sql.get_mcversion(sv['name']) != fb_name:
            for g in (await Sql.get_mcversion('fb_open_group')).split("|"):
                await app.send_group_message(int(g), MessageChain(
                    f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fb_name}\n\n链接：\n{mcfb_json["articles"][0]["html_url"]}'))
            await Sql.change_mcversion(sv['name'], fb_name)
