from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import WildcardMatch, MatchResult, Twilight, RegexMatch
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[
        Twilight([RegexMatch(r'!|！|.|#'),
                  'text' @ WildcardMatch()])]
))
async def menu(app: Ariadne, member: Member, group: Group, message: MessageChain, text: MatchResult):
    if await Sql.is_open(group.id):
        answer = await Sql.get_chatlist(str(text.result))
        if len(answer) != 0:
            await app.send_message(group, answer[0][0])
