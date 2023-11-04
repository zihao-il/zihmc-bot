import random
from datetime import timedelta, datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Face
from graia.ariadne.message.element import Plain
from graia.ariadne.message.formatter import Formatter
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


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("大家晚安")]))
async def every_night(app: Ariadne, group: Group, member: Member):
    if await Sql.is_open(group.id):

        now_time = datetime.now()
        now_time_hour = now_time.hour
        if now_time_hour > 6:
            tomorrow_time = datetime.now() + timedelta(days=1)
            mute_time = datetime(tomorrow_time.year, tomorrow_time.month, tomorrow_time.day, 6, 0, 0)

        else:
            mute_time = datetime(now_time.year, now_time.month, now_time.day, 6, 0, 0)

        m_time = mute_time.timestamp() - now_time.timestamp()
        money = random.randint(100, 200)

        try:
            await app.mute_member(group.id, member.id, int(m_time))
            await Sql.change_money(group.id, member.id, 'Money', money, '+')
            await app.send_message(group, Formatter(
                "{at}\n{face1}晚安，好梦！\n{face2}请放下手机前往被窝\n{face4}晚安奖励{m}蜜桃币\n{face3}明天早上6点见！").format(
                at=At(member.id),
                face1=Face(75),
                face2=Face(8),
                face3=Face(147), face4=Face(304), m=money, ))

        except:
            await app.send_message(group, Formatter(
                "{at}\n{face1}晚安，好梦！\n{face2}请放下手机前往被窝\n{face3}明天早上6点见！").format(at=At(member.id),
                                                                                                    face1=Face(75),
                                                                                                    face2=Face(8),
                                                                                                    face3=Face(147), ))
