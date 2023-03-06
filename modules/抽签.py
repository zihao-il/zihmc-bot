import datetime
import random

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("抽签")], ))
async def lot(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id, 'is_lot'):
        r_num = random.randint(1, 100)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            await Sql.get_group_field('lot_time', group.id, member.id)
        except:
            await Sql.add_qq(group.id, member.id)
        lot_time = await Sql.get_group_field('lot_time', group.id, member.id)
        if now_time != str(lot_time):
            await app.send_message(group, MessageChain([At(member.id), Plain("\n"), await Sql.get_lots(r_num)]), )
            await Sql.update_group_field("lot_time", now_time, group.id, member.id)
        else:
            await app.send_message(group,
                                   MessageChain([At(member.id), Plain("\n每天仅能求一签，若想改运，等到明日再来！")]), )
