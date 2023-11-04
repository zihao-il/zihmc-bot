import asyncio
import datetime
import random

from graia.amnesia.message import MessageChain
from graia.amnesia.message.formatter import Formatter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Face
from graia.ariadne.message.formatter import Formatter
from graia.ariadne.message.parser.base import DetectPrefix, MatchContent, MatchRegex
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch, RegexMatch, MatchResult
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

saya = Saya.current()

channel = Channel.current()
inc = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("存款")]))
async def deposit(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix('存款')):
    if await Sql.is_open(group.id):
        if str(message).isdigit():
            d_money = int(str(message))
            if int(await Sql.get_group_field('Money', group.id, member.id)) >= d_money:
                await Sql.change_money(group.id, member.id, 'Money', d_money, '-')
                if await Sql.is_vip(group.id, member.id):
                    interest = int(d_money * 0.05)
                else:
                    interest = int(d_money * 0.1)
                await Sql.change_money(group.id, member.id, 'bank_money', d_money - interest, '+')
                balance = await Sql.get_group_field('bank_money', group.id, member.id)
                money = await Sql.get_group_field('Money', group.id, member.id)
                await app.send_message(group, MessageChain(
                    ["[🏧] 操作客户：", At(member.id),
                     f'\n[🏧] 操作类型：存款\n[🏧] 存款金额：{d_money}蜜桃币\n[🏧] 手续费用：{interest}蜜桃币\n[🏧] 账户余额：{balance}蜜桃币\n[🏧] 剩余财富：{money}蜜桃币']))

            else:
                await app.send_message(group, MessageChain('存款失败，余额不足！'))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("取款")]))
async def withdraw(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix('取款')):
    if await Sql.is_open(group.id):
        if str(message).isdigit():
            w_money = int(str(message))
            if int(await Sql.get_group_field('bank_money', group.id, member.id)) >= w_money:
                await Sql.change_money(group.id, member.id, 'bank_money', w_money, '-')
                if await Sql.is_vip(group.id, member.id):
                    interest = int(w_money * 0.05)
                else:
                    interest = int(w_money * 0.1)
                await Sql.change_money(group.id, member.id, 'Money', w_money - interest, '+')
                balance = await Sql.get_group_field('bank_money', group.id, member.id)
                money = await Sql.get_group_field('Money', group.id, member.id)
                await app.send_message(group, MessageChain(
                    ["[🏧] 操作客户：", At(member.id),
                     f'\n[🏧] 操作类型：取款\n[🏧] 存款金额：{w_money}蜜桃币\n[🏧] 手续费用：{interest}蜜桃币\n[🏧] 账户余额：{balance}蜜桃币\n[🏧] 剩余财富：{money}蜜桃币']))

            else:
                await app.send_message(group, MessageChain('取款失败，余额不足！'))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("领取利息")]))
async def get_interest(app: Ariadne, member: Member, group: Group, message: MessageChain):
    if await Sql.is_open(group.id):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        interest_time = await Sql.get_group_field('interest_time', group.id, member.id)
        if now_time != str(interest_time):
            bank_money = await Sql.get_group_field('bank_money', group.id, member.id)
            interest = int(bank_money * random.uniform(0.001, 0.01))
            await Sql.update_group_field("interest_time", now_time, group.id, member.id)
            await Sql.change_money(group.id, member.id, 'Money', interest, '+')
            await app.send_message(group,
                                   Formatter("[{gx}] {at}\n[{lq}] {lx}利息\n欢迎存取领取").format(gx=Face(228),
                                                                                                  at=At(member.id),
                                                                                                  lq=Face(308),
                                                                                                  lx=interest, ), )
        else:
            await app.send_message(group, MessageChain('一天只能领取一次！'), )


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('转账'), "at" @ ElementMatch(At), 'money' @ RegexMatch(r"\d+")])], ))
async def transfer(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult,
                   money: MatchResult):
    if await Sql.is_open(group.id):
        if str(member.id) == str(at.result)[1:]:
            await app.send_message(group, MessageChain("无法转账给自己！"))
            return
        await app.send_message(group,
                               Formatter(
                                   "{doge}.交易确认.{doge}\n[汇款人]:{transfer}、\n[收款人]:{collect}\n[转账金额]:{money}蜜桃币\n请回答【是】或者【否】").format(
                                   doge=Face(78),
                                   transfer=At(member.id),
                                   collect=at.result,
                                   money=money.result
                               ), )

        @Waiter.create_using_function([GroupMessage])
        async def is_transfer(g: Group, m: Member, msg: MessageChain):
            if group.id == g.id and member.id == m.id:
                return msg

        try:
            msg = await inc.wait(is_transfer, timeout=60)
        except asyncio.TimeoutError:
            await Sql.change_money(group.id, member.id, 'Money', 100, '-')
            await app.send_message(group, MessageChain("汇款人放弃转账\n收取手续费100蜜桃币"))
        else:
            if str(msg) == '是':
                if int(await Sql.get_group_field('bank_money', group.id, member.id)) >= int(str(money.result)):
                    money = int(str(money.result))
                    await Sql.change_money(group.id, member.id, 'bank_money', money, '-')
                    await Sql.change_money(group.id, str(at.result)[1:], 'bank_money', money - int(money * 0.01), '+')
                    await app.send_message(group,
                                           Formatter(
                                               "{doge}.交易成功.{doge}\n[汇款人]:{transfer}、\n[收款人]:{collect}\n[转账金额]:{money}蜜桃币\n[手续费]:{interest}蜜桃币").format(
                                               doge=Face(78),
                                               transfer=At(member.id),
                                               collect=at.result,
                                               money=money,
                                               interest=int(money * 0.01),
                                           ), )
                else:
                    await app.send_message(group, MessageChain("余额不足，交易失败！"))


            else:
                await Sql.change_money(group.id, member.id, 'Money', 100, '-')
                await app.send_message(group, MessageChain("汇款人放弃转账\n收取手续费100蜜桃币"))


@channel.use(
    ListenerSchema(listening_events=[GroupMessage], decorators=[MatchRegex(regex=r'银行余额|查看存款|银行存款')]))
async def get_bankmoney(app: Ariadne, member: Member, group: Group, message: MessageChain):
    if await Sql.is_open(group.id):
        money = await Sql.get_group_field('bank_money', group.id, member.id)
        await app.send_message(group, MessageChain(f'【银余】：{money}蜜桃币'))


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[
        Twilight([FullMatch('发红包'), 'red_total' @ RegexMatch(r'(\d+)个'), 'red_money' @ RegexMatch(r'\d+'), ])]
))
async def grab_a_red_envelope(app: Ariadne, group: Group, member: Member, message: MessageChain, red_total: MatchResult,
                              red_money: MatchResult):
    if await Sql.is_open(group.id):
        red_total = int(str(red_total.result)[:-1])
        red_money = int(str(red_money.result))
        if await Sql.get_group_field('Money', group.id, member.id) < red_money:
            return await app.send_message(group, MessageChain("余额不足，发红包失败！"))
        await Sql.change_money(group.id, member.id, 'Money', red_money, '-')
        red_num = 0
        get_red_qq = []

        async def distribute_redpacket(total, num):
            result = []
            remain = total
            remain_num = num
            for i in range(1, num):
                average = remain / remain_num
                money = int(random.uniform(0.01, 2 * average))
                result.append(money)
                remain -= money
                remain_num -= 1
            result.append(remain)
            return result

        await app.send_message(group,
                               f'大土豪{member.name}发了{red_total}个总价值为{red_money}蜜桃币的红包\n快来发送“抢红包”来领取红包吧！')
        redpacket_list = await distribute_redpacket(red_money, red_total)

        @Waiter.create_using_function(listening_events=[GroupMessage])
        async def grab_a_red(g: Group, m: Member, msg: MessageChain):
            if group.id == g.id and str(msg) == '抢红包':
                if m.id in get_red_qq:
                    await app.send_message(g, MessageChain([At(m.id), '\n你已经抢过这个红包了！']))
                    return False
                else:
                    get_red_qq.append(m.id)
                    await Sql.change_money(g.id, m.id, 'Money', redpacket_list[red_num], '+')
                    await app.send_message(g, MessageChain(
                        [At(m.id), f'\n恭喜你抢到了{member.name}的红包，获得{redpacket_list[red_num]}蜜桃币']))
                    return True

        while red_num != red_total:
            try:
                msg = await inc.wait(grab_a_red, timeout=1200)
                if msg:
                    red_num += 1
                else:
                    red_num = red_num
            except:
                over_money_list = redpacket_list[red_num:]
                over_money = sum(over_money_list)
                await app.send_message(group, f'退回{member.name}的红包{over_money}蜜桃币！')
                await Sql.change_money(group.id, member.id, 'Money', over_money, '+')
                return
        await app.send_message(group, f'大土豪{member.name}的红包已被领完！')
