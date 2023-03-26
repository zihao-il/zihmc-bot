import asyncio

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


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("来份涩图")]))
async def setu(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) > 0:
            bot_message = await app.send_group_message(group,
                                                       MessageChain(Image(url="https://iw233.cn/api.php?sort=random")))
            await asyncio.sleep(30)
            await app.recall_message(bot_message)
        else:
            await app.send_message(group, MessageChain("丑拒，权限不足！"))
