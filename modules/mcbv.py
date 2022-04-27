from graia.saya import Channel
import json
import re
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

channel = Channel.current()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}

qqgroup = [933238308, 855150997, 562664290, 196619774]


@channel.use(SchedulerSchema(timers.every_custom_minutes(1)))
async def mcbv(app: Ariadne):
    try:
        releasej = requests.get(
            'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001186971/articles?per_page=5',
            headers=headers, timeout=3).text
        releasej = json.loads(releasej)
        betaj = requests.get(
            'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001185332/articles?per_page=5',
            headers=headers, timeout=3).text
        betaj = json.loads(betaj)
        fbr = releasej["articles"][0]["name"]
        fbb = betaj["articles"][0]["name"]
    except:
        pass
    try:
        mcr = requests.get("https://bugs.mojang.com/rest/api/2/project/10200/versions", headers=headers)
        data = json.loads(mcr.text)
        for v in data:
            if not v['archived'] and v['released']:
                if re.match(r".*Beta$", v["name"]):
                    beta = v["name"].split(" ")[0]
                elif re.match(r".*Preview$", v["name"]):
                    preview = v["name"].split(" ")[0]
                else:
                    release = v["name"].split(" ")[0]
    except:
        pass

    path = "data/mc.json"
    with open(path, "r") as mcj:

        mc_data = json.load(mcj)
        try:
            if mc_data['frelease'] != fbr:
                for g in qqgroup:
                    await app.sendGroupMessage(g, MessageChain.create(
                        f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fbr}\n\n链接：\n{releasej["articles"][0]["html_url"]}'))

                mc_data['frelease'] = fbr
            if mc_data['fbeta'] != fbb:
                for g in qqgroup:
                    await app.sendGroupMessage(g, MessageChain.create(
                        f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fbb}\n\n链接：\n{betaj["articles"][0]["html_url"]}'))
                mc_data['fbeta'] = fbb
        except:
            pass

        try:
            if mc_data['release'] != release:
                for g in qqgroup:
                    await app.sendGroupMessage(g, MessageChain.create(f'你有新的正式版请注意查收：\n版本号：{release}'))
                mc_data['release'] = release
            if mc_data['beta'] != beta:
                for g in qqgroup:
                    await app.sendGroupMessage(g, MessageChain.create(f'你有新的测试版请注意查收：\n版本号：{beta}'))
                mc_data['beta'] = beta
            if mc_data['preview'] != preview:
                for g in qqgroup:
                    await app.sendGroupMessage(g, MessageChain.create(f'你有新的预览版请注意查收：\n版本号：{preview}'))
                mc_data['preview'] = preview
        except:
            pass
    with open(path, "w") as mcjup:
        json.dump(mc_data, mcjup)




