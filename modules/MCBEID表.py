from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

# https://ca.projectxero.top/idlist/

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("/id表")]))
async def reload(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix('/id表')):
    session = Ariadne.service.client_session
    try:
        async with session.get(
                f'https://ca.projectxero.top/idlist/search?q={str(message)}&branch=&match=contains') as text:
            json_name = (await text.json())["data"]["result"][0]
    except Exception:
        return await app.send_message(group, [At(member.id), "\n查询失败，没有此数据！"])
    name_data = f'枚举：{json_name["enumName"]}\n条目：{json_name["key"]}\n描述：{json_name["value"]}'
    await app.send_message(group, [At(member.id), f"\n{name_data}"])
