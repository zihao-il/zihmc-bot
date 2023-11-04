from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

saya = Saya.current()

channel = Channel.current()
inc = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("计算")], ))
async def compute(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("计算")):
    if await Sql.is_open(group.id):

        try:
            await app.send_message(group, str(eval(str(message))))
        except:
            pass


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("看图片")], ))
async def lookImg(app: Ariadne, group: Group, member: Member, message: MessageChain):
    @Waiter.create_using_function([GroupMessage])
    async def look_img(g: Group, m: Member, msg: GroupMessage):
        if group.id == g.id and member.id == m.id:
            return msg

    await app.send_group_message(group, "请发送表情包！")
    try:
        msg = await inc.wait(look_img, timeout=120)
    except:
        return

    try:
        link = msg.message_chain[0].url

        await app.send_group_message(group,
                                     MessageChain([Plain(link), Image(url=link)]))
    except:
        await app.send_group_message(group, "发送错误，发送的可能不是图片！")
