import asyncio
import re
import requests
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch, SpacePolicy, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel

channel = Channel.current()




def upcookie(ck):
    with open("data/mtsign.txt", "w+", encoding="utf-8") as cc:
        cc.write(str(ck))
    return "cookie更新成功！"





def mt_sign():
    with open("data/mtsign.txt", "r", encoding="utf-8") as c:
        cookie = c.readline()
    link = "https://bbs.binmt.cc/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash=填自己的"
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; zzz) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36',
        'cookie': cookie
    }
    sign_text = requests.get(url=link, headers=headers).text
    if bool(re.findall(r"您当前的访问请求当中含有非法字符，已经被系统拒绝", sign_text)):
        return 'cookie错误！请发送mt更新cookie"cookie"'
    sign_text = re.findall(r'<root><!\[CDATA\[(.*)]]></root>', sign_text)
    return "mt签到状态：" + sign_text[0]


@channel.use(SchedulerSchema(crontabify("00 6 * * *")))
async def mtsign(app: Ariadne):
    await app.sendGroupMessage(196619774, MessageChain.create(mt_sign()))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("mt重新签到")]))
async def remtsign(app: Ariadne, member: Member, group: Group):
    if member.id == 1767927045:
        await app.sendGroupMessage(group, MessageChain.create(mt_sign()))
    else:
        return


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("mt更新cookie").space(SpacePolicy.NOSPACE),
         WildcardMatch() @ "ucookie"]
    )]
))
async def ucookie(app: Ariadne, group: Group, member: Member, ucookie: MatchResult):
    if member.id == 1767927045:
        ucookie = ucookie.result
        await app.sendMessage(group, MessageChain.create(upcookie(ucookie), "即将为你重新签到！"))
        await asyncio.sleep(1)
        await app.sendGroupMessage(group, MessageChain.create(mt_sign()))
    else:
        return
