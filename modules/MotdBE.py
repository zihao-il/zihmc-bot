import re
import socket
import struct
import time
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import Twilight, WildcardMatch, MatchResult, \
    RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


async def motdbe(ip, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(3)
        start_time = time.time()
        client.sendto(b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx",
                      (ip, port))
        data, addr = client.recvfrom(2048)
        end_time = time.time()
        data = data[1:]
        name_length = struct.unpack(">H", data[32:34])[0]
        decoded_data = data[34: 34 + name_length].decode().split(";")
        delay = "%.2f" % ((end_time - start_time) * 1000)
        client.close()
        msg = f"[{decoded_data[0]}服务器信息]\n描述文本：{decoded_data[1]}\n协议版本：{decoded_data[2]}\n游戏版本：{decoded_data[3]}\n在线人数：{decoded_data[4]}/{decoded_data[5]}\n地图名称：{decoded_data[7]}\n游戏模式：{decoded_data[8]}\n游戏延迟：{delay}ms"
        return msg
    except:
        msg = "查询失败，无此服务器！"
        return msg


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [RegexMatch(r"/MotdBE").flags(re.RegexFlag(re.I)),
         WildcardMatch() @ "ip_port"]
    )]
))
async def motdbemsg(app: Ariadne, group: Group, member: Member, ip_port: MatchResult):
    try:
        ip, port = ip_port.result.split(":")
        ip = str(ip)
        port = int(str(port))
        print(1, type(ip))
        await app.sendMessage(group, MessageChain.create(At(member.id), f"\n", await motdbe(ip, port)))
    except:
        await app.sendMessage(group, MessageChain.create(At(member.id), f"\n格式错误！\n例如：/MotdBE 127.0.0.1:19132"))
