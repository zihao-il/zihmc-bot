import requests
import json
import time
import random

from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel

channel = Channel.current()

headers = {
    "Connection": "close",
    "Host": "floor.huluxia.com",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.8.1"
}

with open("data/hlxsign.txt", "r", encoding="utf-8") as k:
    key = k.readline()


def get_id():
    cid = []

    login_url = f"http://floor.huluxia.com/category/list/ANDROID/2.0?platform=2&gkey=000000&app_version=4.1.1.8.2&versioncode=344&market_id=tool_web&_key={key}&device_code=%5Bd%5Df832b6f8-7727-4fd5-b30c-e58c3c0b90a1&phone_brand_type=MI"
    url_date = requests.get(login_url, headers=headers).text
    json_data = json.loads(url_date)["categories"]

    for i in json_data:
        if i["icon"] != "" and i["title"] != "我的关注" and i["title"] != "三楼活动":
            cid.append(i["categoryID"])
    return cid


def sign():
    try:
        cid = get_id()
    except:
        return "获取板块id错误！\n如需重新签到请发送：三楼重新签到"
    try:
        for sid in cid:
            sign_url = f"http://floor.huluxia.com/user/signin/ANDROID/4.0??platform=2&gkey=000000&app_version=4.1.1.8.2&versioncode=344&market_id=tool_web&_key={key}&device_code=%5Bd%5Df832b6f8-7727-4fd5-b30c-e58c3c0b90a1&phone_brand_type=MI&cat_id={sid}"
            requests.get(sign_url, headers=headers)
            time.sleep(random.randint(5, 10))
    except:
        return "签到发生错误！\n如需重新签到请发送：三楼重新签到"
    return "全部板块已签到成功！"


@channel.use(SchedulerSchema(crontabify("00 6 * * *")))
async def hlxsign(app: Ariadne):
    await app.sendGroupMessage(536765401, MessageChain.create(sign()))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("三楼重新签到")]))
async def rehlxsign(app: Ariadne, member: Member, group: Group):
    if member.id == "1767927045":
        await app.sendGroupMessage(group, MessageChain.create(sign()))
    else:
        return
