from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def get_nudge(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group":
        if await Sql.is_open(event.group_id):
            await app.send_group_message(
                event.group_id,
                MessageChain("不要戳我QAQ")
            )
    elif event.context_type == "friend":
        await app.send_friend_message(
            event.friend_id,
            MessageChain("戳我干嘛！")
        )
    else:
        return


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("戳我")], ))
async def nudge_me(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        await app.send_nudge(member.id, group.id)
