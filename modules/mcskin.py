import asyncio
import base64
import json
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import FullMatch, Twilight, SpacePolicy, WildcardMatch, MatchResult
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

saya = Saya.current()
channel = Channel.current()
inc = InterruptControl(saya.broadcast)


def getuuid(mcid):
    uuid = requests.get('https://api.mojang.com/users/profiles/minecraft/' + mcid).text
    uuid = json.loads(uuid)['id']
    return uuid

def getskin(uuid):
        skinj = requests.get('https://sessionserver.mojang.com/session/minecraft/profile/'+uuid).text
        skinj = json.loads(skinj)
        b64 = skinj['properties'][0]['value']
        scurl = base64.b64decode(b64).decode("utf-8", "ignore")
        scurl = json.loads(scurl)
        skinurl = scurl['textures']['SKIN']['url']
        try:
            capeurl = scurl['textures']['CAPE']['url']
        except:
            return skinurl
        return skinurl,capeurl


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("皮肤获取").space(SpacePolicy.FORCE),
         WildcardMatch() @ "mcid"]
    )]
))
async def mcname(app: Ariadne, group: Group, member: Member,mcid: MatchResult):
    mcid = mcid.result.replace(" ","")
    try:
        uuid = getuuid(str(mcid))
    except:
        await app.sendMessage(group, MessageChain.create("查无此人"))
        return
    skinurl = getskin(uuid)

    if len(skinurl) == 2:
        await app.sendMessage(
            group,
            MessageChain.create(
                Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
                Image(url=skinurl[0]),
                Plain("\n披风："),
                Image(url=skinurl[1]),
            ),
        )
    else:
        await app.sendMessage(
            group,
            MessageChain.create(
                Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
                Image(url=skinurl),
            ),
        )


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
        try:
            uuid = getuuid(str(mcid))
        except:
            await app.sendMessage(group, MessageChain.create("查无此人"))
            return
        skinurl = getskin(uuid)

        if len(skinurl) == 2:
            await app.sendMessage(
                group,
                MessageChain.create(
                    Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
                    Image(url=skinurl[0]),
                    Plain("\n披风："),
                    Image(url=skinurl[1]),
                ),
            )
        else:
            await app.sendMessage(
                group,
                MessageChain.create(
                    Plain("名字: " + mcid.asDisplay() + "\n皮肤："),
                    Image(url=skinurl),
                ),
            )
