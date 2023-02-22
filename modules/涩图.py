import asyncio

import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("来份涩图")]))
async def setu(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) > 0:
            r = requests.get("https://iw233.cn/api.php?sort=random", allow_redirects=False).headers.get('Location')
            bot_message = await app.send_message(group, MessageChain(Image(url=r)))
            await asyncio.sleep(30)
            await app.recall_message(bot_message)
        else:
            await app.send_message(group, MessageChain("丑拒，权限不足！"))
