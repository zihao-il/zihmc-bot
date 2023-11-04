import re
import uuid
from datetime import timedelta, datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, MatchResult, FullMatch
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('生成积分卡密'), "types" @ RegexMatch(r"单充卡|多充卡"),
                                 'ct' @ RegexMatch(r"\d+"), FullMatch('个'), 'money' @ RegexMatch(r"\d+")])], ))
async def create_kami(app: Ariadne, member: Member, group: Group, types: MatchResult,
                      money: MatchResult, ct: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) < 2:
            return await app.send_message(group, '丑拒，权限不足！')
        await app.send_message(group, '生成中，请稍后查看私聊...')

        text = f'🔑=======积分卡密=======🔑\n'
        if str(types.result) == '单充卡':
            for i in range(int(str(ct.result))):
                u = str(uuid.uuid4())
                text += f"卡密：{u}\n积分：{str(money.result)}    可用次数：1\n\n"
                await Sql.add_kami(u, 'money', int(str(money.result)), 1)
        elif str(types.result) == '多充卡':
            u = str(uuid.uuid4())
            text += f"卡密：{u}\n积分：{str(money.result)}    可用次数：{str(ct.result)}\n"
            await Sql.add_kami(u, 'money', int(str(money.result)), int(str(ct.result)))

        await app.send_friend_message(member.id, text)


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight(
                           [RegexMatch(r'生成会员卡密|生成vip卡密').flags(re.I), "types" @ RegexMatch(r"单充卡|多充卡"),
                            'ct' @ RegexMatch(r"\d+"), FullMatch('个'), "vip_num" @ RegexMatch(r"\d+"),
                            'vip_name' @ RegexMatch(r'天|个月|年')])], ))
async def create_kami(app: Ariadne, member: Member, group: Group, types: MatchResult,
                      ct: MatchResult, vip_num: MatchResult, vip_name: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) < 2:
            return await app.send_message(group, '丑拒，权限不足！')

        await app.send_message(group, '生成中，请稍后查看私聊...')
        vip_num = int(str(vip_num.result))
        vip_name = str(vip_name.result)
        vip_time = 0
        if vip_name == "天":
            vip_time = 86400 * vip_num
        elif vip_name == "个月":
            vip_time = 2592000 * vip_num
        elif vip_name == "年":
            vip_time = 31536000 * vip_num
        text = f'🔑=======会员卡密=======🔑\n'
        if str(types.result) == '单充卡':
            for i in range(int(str(ct.result))):
                u = str(uuid.uuid4())
                text += f"卡密：{u}\n时长：{vip_num}{vip_name}   可用次数：1\n\n"
                await Sql.add_kami(u, 'vip', vip_time, 1)
        elif str(types.result) == '多充卡':
            u = str(uuid.uuid4())
            text += f"卡密：{u}\n时长：{vip_num}{vip_name}    可用次数：{str(ct.result)}\n"
            await Sql.add_kami(u, 'vip', vip_time, int(str(ct.result)))

        await app.send_friend_message(member.id, text)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("卡密充值")]))
async def exchange_kami(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix('卡密充值')):
    if await Sql.is_open(group.id):
        kami_info = await Sql.get_kami(message)
        if len(kami_info) == 0:
            return await app.send_message(group, MessageChain([At(member.id), Plain(f"\n充值失败，无效的卡密！")]), )
        if kami_info[0][3] > 0:
            if str(member.id) in str(kami_info[0][4]).split('|'):
                return await app.send_message(group, MessageChain(
                    [At(member.id), Plain(f"\n你已经充值过此卡密，无法再次充值！")]), )
            await Sql.change_kami(message)
            await Sql.add_kami_qq(message, member.id)
            if kami_info[0][3] == 1:
                await Sql.del_kami(message)

            if kami_info[0][1] == 'money':
                await Sql.change_money(group.id, member.id, 'Money', kami_info[0][2], '+')
                await app.send_message(group,
                                       MessageChain(
                                           [At(member.id), Plain(f"\n兑换成功，获得{kami_info[0][2]}蜜桃币！")]), )
            elif kami_info[0][1] == 'vip':
                if await Sql.is_vip(group.id, member.id):
                    await Sql.change_money(group.id, member.id, 'vip_time', kami_info[0][2], '+')
                else:
                    add_vip_time = datetime.timestamp(datetime.now()) + kami_info[0][2]
                    await Sql.set_money(group.id, member.id, 'vip_time', add_vip_time)
                vip_time = datetime.strftime(
                    datetime.fromtimestamp(await Sql.get_group_field('vip_time', group.id, member.id)),
                    '%Y-%m-%d %H:%M:%S')
                time = timedelta(seconds=kami_info[0][2])
                await app.send_message(group,
                                       MessageChain([At(member.id),
                                                     Plain(f"\n兑换成功，获得时长{time}\n会员到期时长为：{vip_time}")]), )
