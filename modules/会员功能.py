import re
from datetime import datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchRegex
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, \
    MatchResult
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight(
                           [RegexMatch(r'购买会员|购买vip').flags(re.I), "vip_num" @ RegexMatch(r"\d+", optional=True),
                            'vip_name' @ RegexMatch(r'个月|年', optional=True)])], ))
async def buy_vip(app: Ariadne, member: Member, group: Group, vip_num: MatchResult, vip_name: MatchResult):
    if await Sql.is_open(group.id):
        buy_money = await Sql.get_vipmoney(group.id)
        if vip_name.result is None or vip_num.result is None:
            if vip_name.result is None and vip_num.result is None:
                vip_money = buy_money
                vip_time = 2592000
            else:
                return

        else:
            vip_num = int(str(vip_num.result))
            vip_name = str(vip_name.result)
            if vip_name == "个月":
                vip_money = buy_money * vip_num
                vip_time = 2592000 * vip_num
            elif vip_name == "年":
                vip_money = buy_money * vip_num * 12
                vip_time = 31536000 * vip_num
        money = await Sql.get_group_field('Money', group.id, member.id)
        if money < vip_money:
            await app.send_message(group,
                                   MessageChain([At(member.id), Plain(f"\n蜜桃币不足！\n需要{vip_money}蜜桃币")]), )
        else:
            await Sql.change_money(group.id, member.id, 'Money', vip_money, '-')

            if await Sql.is_vip(group.id, member.id):  # 是会员加时长
                await Sql.change_money(group.id, member.id, 'vip_time', vip_time, '+')
                vip_expired_time = datetime.strftime(
                    datetime.fromtimestamp(await Sql.get_group_field('vip_time', group.id, member.id)),
                    '%Y-%m-%d %H:%M:%S')
                await app.send_message(group,
                                       MessageChain(
                                           [At(member.id), Plain(f"\n购买成功！\n会员到期时间：{vip_expired_time}")]), )

            else:
                add_vip_time = datetime.timestamp(datetime.now()) + vip_time
                vip_expired_time = datetime.strftime(datetime.fromtimestamp(add_vip_time), '%Y-%m-%d %H:%M:%S')
                await Sql.set_money(group.id, member.id, 'vip_time', add_vip_time)
                await app.send_message(group,
                                       MessageChain(
                                           [At(member.id), Plain(f"\n购买成功！\n会员到期时间：{vip_expired_time}")]), )


@channel.use(ListenerSchema(listening_events=[GroupMessage],
                            decorators=[MatchRegex(regex=r'会员到期时间|vip到期时间', flags=re.RegexFlag(re.I))]))
async def get_viptime(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        vip_time = datetime.strftime(
            datetime.fromtimestamp(await Sql.get_group_field('vip_time', group.id, member.id)),
            '%Y-%m-%d %H:%M:%S')
        await app.send_message(group,
                               MessageChain([At(member.id), Plain(f"\n你的会员到期时间为：\n{vip_time}")]), )
