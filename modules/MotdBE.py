import re
import socket
import struct
import time

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, MatchResult, WildcardMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


async def motd_be(ip: str, port: int = 19132):
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
        if decoded_data[8].lower() == "Survival".lower():
            gamemode = "生存模式"
        elif decoded_data[8].lower() == "Creative".lower():
            gamemode = "创造模式"
        elif decoded_data[8].lower() == "Adventure".lower():
            gamemode = "冒险模式"
        else:
            gamemode = "未知模式"
        msg = f"[{decoded_data[0]}服务器信息]\n描述文本：{decoded_data[1]}\n协议版本：{decoded_data[2]}\n游戏版本：{decoded_data[3]}\n在线人数：{decoded_data[4]}/{decoded_data[5]}\n地图名称：{decoded_data[7]}\n游戏模式：{gamemode}\n游戏延迟：{delay}ms"
        return msg
    except:
        msg = "查询失败，无此服务器！"
        return msg


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([RegexMatch(r'/MotdBE').flags(re.I), "ipaddr" @ WildcardMatch(), ])], ))
async def get_be_motd(app: Ariadne, group: Group, member: Member, message: MessageChain, ipaddr: MatchResult):
    if await Sql.is_open(group.id):
        try:
            ip_port = str(ipaddr.result)
            if bool(re.findall(":", ip_port)):
                ip, port = ip_port.split(":")
                ip = str(ip)
                port = int(str(port))
            else:
                ip = str(ip_port)
                port = 19132

            await app.send_message(group, await motd_be(ip, port))
        except:
            pass
