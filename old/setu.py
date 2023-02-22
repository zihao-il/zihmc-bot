import requests
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image, Voice, At
import asyncio
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema


channel = Channel.current()

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("来一份涩图")]))
async def setu(app: Ariadne, member: Member, group: Group):
    if group.id not in [562664290]:
        await app.sendMessage(group, MessageChain.create("对不起，该群并不能发涩图"))
    elif member.id not in [1767927045]:
        await app.sendMessage(group, MessageChain.create(At(member.id), "对不起，您的权限并不够"))
    else:
        r = requests.get("https://iw233.cn/api.php?sort=random", allow_redirects=False).headers.get('Location')
        bot_message = await app.sendMessage(group, MessageChain.create(Image(url=r)))
        await asyncio.sleep(30)
        await app.recallMessage(bot_message)
