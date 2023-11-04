import datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.base import MatchContent, MatchRegex
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("你好")]))
async def hello(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        now = datetime.datetime.now()
        text = ''
        if 0 < now.hour <= 6:
            text = '你好，这么晚了还不休息想干什么？'
        elif 6 < now.hour <= 12:
            text = '上午好呀，吃饭了吗？嘤嘤嘤'
        elif 12 < now.hour <= 18:
            text = '下午好呀，吃饭了吗？嘤嘤嘤'
        elif 18 < now.hour <= 24:
            text = '晚上好呀，吃饭了吗？嘤嘤嘤'
        await app.send_message(group, MessageChain([At(member.id), f'，{text}']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("嘤嘤嘤")]))
async def yyy(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain([At(member.id), f'，一拳一个嘤嘤怪']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("时间")]))
async def now_time(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        await app.send_message(group, MessageChain([At(member.id), f'，当前时间：{time}']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchRegex(regex=r'早|早安')]))
async def zao(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain([At(member.id), f'，早安，记得多喝热水哦~']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("午安")]))
async def wu(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain([At(member.id), f'，中午好，要吃饱饱的哦~']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("晚安")]))
async def wan(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain([At(member.id), f'，晚安，早点休息哦~']))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("杂鱼")]))
async def wan(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        await app.send_message(group, MessageChain([At(member.id), f'，杂鱼❤️~杂鱼❤️~']))
