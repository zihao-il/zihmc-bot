import asyncio
import json

import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, SpacePolicy, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler.timers import crontabify

channel = Channel.current()

with open("data/shouersign.txt", "r", encoding="utf-8") as k:
    key = k.readline()
    appid, authorization = key.split("+")


def upkey(nkey):
    with open("data/shouersign.txt", "w+", encoding="utf-8") as kk:
        kk.write(str(nkey))
        key = kk.readline()
        appid, authorization = key.split("+")
    return "Appid跟Authorization更新成功！"


headers = {
    "Cache-Control": "no-cache",
    "AppID": appid,
    "Version": "3.3.4",
    "Authorization": authorization,
    "Host": "api1.mimikko.cn",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1",
}

sign_link = "https://api1.mimikko.cn/client/RewardRuleInfo/SignAndSignInformationV3"
exp_link = "https://api1.mimikko.cn/client/love/ExchangeReward?code=momona"


async def srsign():
    sign_day = requests.get(sign_link, headers=headers).text
    sign_json = json.loads(sign_day)
    if sign_json["code"] != "0":
        return sign_json["msg"]
    msg = [
        Plain(f'获得的好感度：{sign_json["body"]["Reward"]}\n'),
        Plain(f'{sign_json["body"]["Description"]}\n{sign_json["body"]["Name"]}\n'),
        Image(url=f'{sign_json["body"]["PictureUrl"]}'),
    ]
    return msg


async def srexp():
    exp_day = requests.get(exp_link, headers=headers).text
    exp_json = json.loads(exp_day)
    if exp_json["code"] != "0":
        return exp_json["msg"]
    return f'兑换成功：{exp_json["body"]["Favorability"]}/{exp_json["body"]["MaxFavorability"]}'


@channel.use(SchedulerSchema(crontabify("00 6 * * *")))
async def souersign(app: Ariadne):
    await app.sendGroupMessage(196619774, MessageChain.create(await srsign()))
    await app.sendGroupMessage(196619774, MessageChain.create(await srexp()))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("兽耳重新签到")]))
async def resrsign(app: Ariadne, member: Member, group: Group):
    if member.id == 1767927045:
        await app.sendGroupMessage(196619774, MessageChain.create(await srsign()))
        await app.sendGroupMessage(196619774, MessageChain.create(await srexp()))
    else:
        return


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("兽耳更新key").space(SpacePolicy.NOSPACE),
         WildcardMatch() @ "ukey"]
    )]
))
async def udkey(app: Ariadne, group: Group, member: Member, ukey: MatchResult):
    if member.id == 1767927045:
        ukey = ukey.result.replace(" ", "")
        await app.sendMessage(group, MessageChain.create(upkey(ukey), "即将为你重新签到！"))
        await asyncio.sleep(3)
        await app.sendGroupMessage(196619774, MessageChain.create(await srsign()))
        await app.sendGroupMessage(196619774, MessageChain.create(await srexp()))
    else:
        return
