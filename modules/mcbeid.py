import requests
import json
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.ariadne.message.parser.twilight import FullMatch, Twilight, SpacePolicy, WildcardMatch, MatchResult
from graia.ariadne.model import Group, Member
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

# https://ca.projectxero.top/idlist/

channel = Channel.current()

def get_json(name):
    try:
        id_data = requests.get(f"https://ca.projectxero.top/idlist/search?q={name}&branch=translator&match=startswith").text
        json_name = json.loads(id_data)["data"]["result"][0]
    except:
        return "查询失败，没有此数据！！"
    name_data = f'枚举：{json_name["enumName"]}\n条目：{json_name["key"]}\n描述：{json_name["value"]}'
    return name_data


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("/id表").space(SpacePolicy.NOSPACE),
         WildcardMatch() @ "mcid"]
    )]
))
async def mcname(app: Ariadne, group: Group, member: Member,mcid: MatchResult):
    mcid = mcid.result.replace(" ", "")
    await app.sendMessage(group, MessageChain.create(At(member.id), "\n", get_json(mcid)))
