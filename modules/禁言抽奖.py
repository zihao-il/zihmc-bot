import random
from datetime import timedelta

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("禁言抽奖")]))
async def mute(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        mute_time = random.randint(0, 7200)
        text = ''
        if mute_time == 0 and mute_time == 7200:
            text = 'NB'
        elif mute_time < 1800:
            text = '傻瓜'
        elif mute_time < 3600:
            text = '憨憨'
        elif mute_time < 5400:
            text = '笨蛋'
        elif mute_time < 7200:
            text = '蠢货'
        hours_time = timedelta(seconds=mute_time)
        try:
            await app.mute_member(group.id, member.id, mute_time)
            await app.send_message(group, MessageChain(
                [At(member.id), Plain(f"\n恭喜中奖！\n本次结果为：{text}\n获得时长：{hours_time}")]), )
        except:
            await app.send_message(group,
                                   MessageChain([At(member.id), Plain(f"\n抽奖失败，无法禁言！")]), )
