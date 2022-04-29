import asyncio
import base64
import json
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import FullMatch, Twilight, SpacePolicy, WildcardMatch, MatchResult
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

saya = Saya.current()
channel = Channel.current()
inc = InterruptControl(saya.broadcast)

def getskin(mcid):
    try:
        uuid = requests.get('https://api.mojang.com/users/profiles/minecraft/' + mcid).text
        uuid = json.loads(uuid)['id']
    except:
        msg = [
            Plain("获取失败！用户不存在"),
        ]
        return msg
    skinj = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/'+uuid).text
    skinj = json.loads(skinj)
    b64 = skinj['properties'][0]['value']
    scurl = base64.b64decode(b64).decode("utf-8", "ignore")
    scurl = json.loads(scurl)
    skinurl = scurl['textures']['SKIN']['url']
    try:
        capeurl = scurl['textures']['CAPE']['url']
    except:
        msg = [
            Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
            Image(url=skinurl),
        ]
        return msg
    msg = [
        Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
        Image(url=skinurl),
        Plain("\n披风："),
        Image(url=capeurl),
    ]
    return msg

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("皮肤获取").space(SpacePolicy.FORCE),
         WildcardMatch() @ "mcid"]
    )]
))
async def mcname(app: Ariadne, group: Group, member: Member,mcid: MatchResult):
    mcid = mcid.result.replace(" ","")
    await app.sendMessage(group, MessageChain.create(getskin(mcid)))

@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("皮肤获取")]))
async def mcname(app: Ariadne, group: Group, member: Member):
    await app.sendMessage(group, MessageChain.create("请发送用户名："))

    @Waiter.create_using_function([GroupMessage])
    async def getmcskin(g: Group, m: Member, msg: MessageChain):
        if group.id == g.id and member.id == m.id:
            return msg
    try:
        mcid = await inc.wait(getmcskin, timeout=30)
    except asyncio.TimeoutError:
        await app.sendMessage(group, MessageChain.create("超时了，请重新发送"))
    else:
        await app.sendMessage(group, MessageChain.create(getskin(mcid)))
