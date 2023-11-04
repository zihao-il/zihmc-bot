import datetime
import random

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import Waiter, InterruptControl
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

saya = Saya.current()

channel = Channel.current()
inc = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("抽签")], ))
async def lot(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id, 'is_lot'):
        r_num = random.randint(1, 100)
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            await Sql.get_qqlist(member.id, 'lot_time')
        except:
            await Sql.add_qqlist(member.id)
        lot_time = await Sql.get_qqlist(member.id, 'lot_time')
        if now_time != str(lot_time):
            lot_txt = await Sql.get_lots(r_num)
            await app.send_message(group, MessageChain([At(member.id), Plain("\n"), lot_txt]), )
            await Sql.update_qqlist(member.id, "lot_time", now_time)
            if lot_txt[:2] == "下签":
                await app.send_message(group, MessageChain(
                    [At(member.id), Plain("\n"), "很遗憾，你抽到了下签，是否要选择花蜜桃币烧香祈福呢？（是/否？）"]), )

                @Waiter.create_using_function([GroupMessage])
                async def q_lot(g: Group, m: Member, msg: MessageChain):
                    if group.id == g.id and member.id == m.id:
                        return msg

                try:
                    msg = await inc.wait(q_lot, timeout=60)
                except:
                    return
                if str(msg) == "是":
                    if await Sql.get_group_field('Money', group.id, member.id) < 100:
                        return await app.send_message(group,
                                                      MessageChain(
                                                          [At(member.id), Plain(f"\n蜜桃币不足！\n无法进行祈福")]), )
                    await Sql.change_money(group.id, member.id, 'Money', 100, '-')
                    await app.send_message(group, "谢谢你的祈福，亲爱的！祝你度过一个超级可爱的一天，充满快乐和惊喜哦！😊🌟")

        else:
            await app.send_message(group,
                                   MessageChain([At(member.id), Plain("\n每天仅能求一签，若想改运，等到明日再来！")]), )
