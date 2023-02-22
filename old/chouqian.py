import configparser
import datetime
import random
import re
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image, Voice, At
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()

jpath = "data/抽签记录.ini"
qpath = "data/抽签.txt"

config = configparser.ConfigParser()
config.read(jpath, encoding='utf-8')


def get_text(num):
    with open(qpath, "r", encoding='utf-8') as cq:
        line = cq.read()
        text = re.findall(f'{num}\n(.*)\n{num + 1}\n', line, re.S)
    return text


def cq(qqid):
    rnum = random.randint(1, 100)
    now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        old_time = config.get('抽签记录', qqid)
        if now_time != old_time:
            config['抽签记录'][qqid] = now_time
            text = get_text(rnum)[0]
            config.write()
            return text
        else:
            return "每天仅能求一签，若想改运，等到明日再来！"
    except:
        config.set('抽签记录', qqid, now_time)
        config.write(open(jpath, mode='w', encoding='utf-8'))
        text = get_text(rnum)[0]
        return text


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("抽签")]))
async def chouqian(app: Ariadne, member: Member, group: Group):
    await app.sendMessage(group, MessageChain.create(At(member.id), "\n", cq(str(member.id))))
