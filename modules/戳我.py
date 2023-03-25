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
    if event.target == (await app.get_bot_list())[0]:
        if await Sql.is_open(event.subject['id']):
            if event.subject['kind'] == "Group" and app.default_account == event.target:

                try:
                    await app.mute_member(event.subject['id'], event.supplicant, 15)
                except:
                    pass
                return await app.send_group_message(
                    event.subject['id'], "不要戳我QAQ")

        if event.subject['kind'] == "Friend":
            return await app.send_friend_message(
                event.subject['id'], "戳我干嘛！")


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("戳我")], ))
async def nudge_me(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        await app.send_nudge(member.id, group.id)
