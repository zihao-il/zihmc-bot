import csv
import datetime

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Face
from graia.ariadne.message.formatter import Formatter
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def open_group(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        await Sql.change_money(group.id, member.id, 'say_num', 1, '+')
    if await Sql.is_founder(member.id):
        if message.display == "初始化":
            if await Sql.is_open(group.id, 'is_init'):
                await app.send_message(group, MessageChain(Face(187), f'本群已初始化过！'), )
            else:
                if await Sql.create_table(group.id):
                    await Sql.add_group(group.id)
                    await app.send_message(group,
                                           MessageChain(Face(329), f'初始化成功！\n如要开启本群请发送"开启本群"'), )
                else:
                    await app.send_message(group, MessageChain(Face(328), f'初始化失败！'), )

        if message.display == "开启本群":
            if not await Sql.is_open(group.id):
                if await Sql.change_group_open(group.id, 1):
                    await app.send_message(group,
                                           Formatter("{name}({id})\n{face}开启成功！").format(name=group.name,
                                                                                             id=group.id,
                                                                                             face=Face(329)), )
                else:
                    await app.send_message(group, MessageChain(Face(328), f'本群未初始化！'), )

        if message.display == "关闭本群":
            if await Sql.is_open(group.id):
                if await Sql.change_group_open(group.id, 0):
                    await app.send_message(group,
                                           Formatter("{name}({id})\n{face}关闭成功！").format(name=group.name,
                                                                                             id=group.id,
                                                                                             face=Face(328)), )
                else:
                    await app.send_message(group, MessageChain(Face(328), f'本群已经关闭！'), )


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ban_word(app: Ariadne, event: GroupMessage, group: Group, message: MessageChain):
    if await Sql.is_open(group.id):
        _ban_word = (await Sql.select_open("ban_word", "qq_group", event.sender.group.id))[0][0]
        ban_word_list = _ban_word.split("|")
        for word in ban_word_list:
            if word in str(message).lower():
                try:
                    await app.recall_message(event, group)
                    await app.send_message(group, '发现违禁词！已撤回处理！')
                    break
                except:
                    break


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def save_msg(app: Ariadne, event: GroupMessage):
    today = datetime.datetime.now()
    path = f"data/msg/{today.isocalendar()[0]}-{today.isocalendar()[1]}.csv"

    li = [[event.source.time, event.sender.group.id, event.sender.group.name, event.sender.id, event.sender.name,
           repr(str(event.message_chain))]]

    with open(path, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        for i in li:
            w.writerow(i)
