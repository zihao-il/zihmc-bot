import base64
import json

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, RegexMatch, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


async def get_skin(mcid):
    session = Ariadne.service.client_session
    try:
        async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{mcid}") as text:
            get_id = await text.json()
        name = get_id['name']
        uuid = get_id['id']

    except:
        msg = [
            Plain(f'获取失败！没有此用户："{mcid}"'),
        ]
        return msg
    async with session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as text:
        skinj = await text.json()
    b64 = skinj['properties'][0]['value']
    scurl = base64.b64decode(b64).decode("utf-8", "ignore")
    scurl = json.loads(scurl)
    skinurl = scurl['textures']['SKIN']['url']
    try:
        capeurl = scurl['textures']['CAPE']['url']
    except:
        msg = [
            Plain("名字: " + name + "\n皮肤："),
            Image(url=skinurl),
        ]
        return msg
    msg = [
        Plain("名字: " + name + "\n皮肤："),
        Image(url=skinurl),
        Plain("\n披风："),
        Image(url=capeurl),
    ]
    return msg


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('皮肤获取'), 'mc_name' @ RegexMatch(r"\w+")])], ))
async def get_mcskin(app: Ariadne, group: Group, member: Member, message: MessageChain, mc_name: MatchResult):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain(await get_skin(mc_name.result)))
