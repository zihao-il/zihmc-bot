from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MentionMe()]))
async def chat(app: Ariadne, member: Member, group: Group, message: MessageChain = MentionMe()):
    if await Sql.is_open(group.id):
        url = 'http://openapi.turingapi.com/openapi/api/v2'
        data = {
            "reqType": 0,
            "perception": {
                "inputText": {
                    "text": str(message)
                },
            },
            "userInfo": {
                "apiKey": "阿巴巴",
                "userId": "阿巴阿巴"
            }
        }
        if str(message) == "":
            return await app.send_message(group, f'我是萌萌的机器人，叫我有什么吩咐吗，嘤嘤嘤', )
        session = Ariadne.service.client_session
        async with session.post(url, json=data) as resp:
            r = (await resp.json(content_type='text/plain'))['results'][0]['values']['text']
        await app.send_message(group,
                               MessageChain(r), )
