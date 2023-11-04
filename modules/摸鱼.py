import asyncio
import random

from graia.amnesia.message import MessageChain
from graia.amnesia.message.formatter import Formatter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Face
from graia.ariadne.message.element import Plain
from graia.ariadne.message.formatter import Formatter
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[
        Twilight([RegexMatch(r'^摸鱼\d+次'), ])]
))
async def m_fish(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        m_num = int(str(message)[2:-1])
        if int(m_num) <= 0:
            return
        if await Sql.get_group_field('Money', group.id, member.id) < m_num * 200:
            return await app.send_message(group,
                                          MessageChain([At(member.id), Plain(f"\n蜜桃币不足！\n无法摸{m_num}次鱼")]), )
        await Sql.change_money(group.id, member.id, 'Money', m_num * 200, '-')
        await app.send_message(group, MessageChain(f"摸鱼中...请稍等..."), )
        random_time = random.randint(1, 30)
        await asyncio.sleep(random_time)

        get_money = 0
        fish_num = {"七彩大咸鱼": 0, "金色咸鱼": 0, "大咸鱼": 0, "咸鱼": 0, }
        for i in range(m_num):
            win_num = random.randint(0, 1000)
            if win_num == 0 or win_num == 1000:
                get_money += 20000
                fish_num["七彩大咸鱼"] += 1
            elif win_num < 10:
                get_money += 2000
                fish_num["金色咸鱼"] += 1
            elif win_num < 100:
                get_money += 200
                fish_num["大咸鱼"] += 1
            else:
                get_money += 20
                fish_num["咸鱼"] += 1
        text = '摸鱼成功！\n摸到以下的鱼：\n'
        for key, value in fish_num.items():
            if value != 0:
                text += f'{key}：{value}条\n'
        await Sql.set_fish(group.id, member.id, fish_num["七彩大咸鱼"], fish_num["金色咸鱼"], fish_num["大咸鱼"],
                           fish_num["咸鱼"])
        await app.send_message(group,
                               Formatter('{at}\n{face}{text}\n{face2}共获得{m}蜜桃币').format(at=At(member.id),
                                                                                              face=Face(285),
                                                                                              text=text,
                                                                                              m=str(get_money),
                                                                                              face2=Face(
                                                                                                  293), ), )
        await Sql.change_money(group.id, member.id, 'Money', get_money, '+')


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("摸鱼记录")], ))
async def g_fish(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        date = await Sql.get_fish(group.id, member.id)
        if len(date) == 0:
            await app.send_message(group,
                                   MessageChain([At(member.id), "\n你还没有", Face(285)]), )
        await app.send_message(group,
                               Formatter(
                                   '{at}\n{face}摸鱼记录如下：\n七彩大咸鱼：{f1}条\n金色咸鱼：{f2}条\n大咸鱼：{f3}条\n咸鱼：{f4}条\n').format(
                                   at=At(member.id),
                                   f1=date[0][0],
                                   f2=date[0][1],
                                   f3=date[0][2],
                                   f4=date[0][3],
                                   face=Face(285), ), )


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("摸鱼排行榜")]))
async def fish_list(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        msg = """————摸鱼排行榜————
🐟咸鱼排行榜
🐟大咸鱼排行榜
🐟金色咸鱼排行榜
🐟七彩大咸鱼排行榜
————————————"""
        await app.send_message(group, msg)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("领取摸鱼成就")]))
async def grab_a_red_envelope(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        date = await Sql.get_fish(group.id, member.id)
        if len(date) == 0:
            await app.send_message(group,
                                   MessageChain([At(member.id), "\n你还没有", Face(285)]), )
        fish_all_list = {
            0: ['萌新级七彩大咸鱼', '专家级七彩大咸鱼', '大师级七彩大咸鱼', '宗师级七彩大咸鱼', '传说级七彩大咸鱼'],
            1: ['萌新级金色咸鱼', '专家级金色咸鱼', '大师级金色咸鱼', '宗师级金色咸鱼', '传说级金色咸鱼'],
            2: ['萌新级大咸鱼', '专家级大咸鱼', '大师级大咸鱼', '宗师级大咸鱼', '传说级大咸鱼'],
            3: ['萌新级咸鱼', '专家级咸鱼', '大师级咸鱼', '宗师级咸鱼', '传说级咸鱼'], }
        fish_text = ''

        async def get_fish_title(data_num, d):
            if data_num >= 10000000 / d:
                list_id = 4
            elif data_num >= 1000000 / d:
                list_id = 3
            elif data_num >= 100000 / d:
                list_id = 2
            elif data_num >= 10000 / d:
                list_id = 1
            elif data_num >= 1000 / d:
                list_id = 0
            else:
                return
            return list_id

        for k, v in fish_all_list.items():
            fish_list = v
            if k == 0:
                m = 1000
            elif k == 1:
                m = 100
            elif k == 2:
                m = 10
            elif k == 3:
                m = 1
            else:
                m = 0

            fish = await get_fish_title(date[0][k], m)
            if fish == None:
                continue
            treasure_data = await Sql.get_group_field('treasure_data', group.id, member.id)
            if treasure_data is None:
                treasure_data_list = []
            else:
                treasure_data_list = treasure_data.split("|")
            for i in range(0, fish + 1):
                try:
                    treasure_data_list.remove(fish_list[i])
                except:
                    pass
            treasure_data_list.append(fish_list[fish])
            fish_text += f'{fish_list[fish]}\n'
            treasure_data_join = '|'.join(treasure_data_list)
            await Sql.set_money(group.id, member.id, 'treasure_data', treasure_data_join)

        a_list = [10000, 1000, 100, 10, 1]
        m_num = 0
        for i in a_list:
            fish_list = ['究极摸鱼怪', '摸鱼怪', '摸鱼大亨', '摸鱼专家', '摸鱼收藏家', ]
            if date[0][0] >= i and date[0][1] >= i and date[0][2] >= i and date[0][3] >= i:
                treasure_data = await Sql.get_group_field('treasure_data', group.id, member.id)
                if treasure_data is None:
                    treasure_data_list = []
                else:
                    treasure_data_list = treasure_data.split("|")
                try:
                    treasure_data_list.remove(fish_list[m_num])
                except:
                    pass
                treasure_data_list.append(fish_list[m_num])
                fish_text += f'{fish_list[m_num]}\n'
                treasure_data_join = '|'.join(treasure_data_list)
                await Sql.set_money(group.id, member.id, 'treasure_data', treasure_data_join)
                break
            m_num += 1
        await app.send_message(group, MessageChain([At(member.id), f'恭喜你获得以下成就\n{fish_text}']))
