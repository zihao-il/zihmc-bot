import json
import re
import socket
import struct
import time

import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import Twilight, WildcardMatch, MatchResult, \
    RegexMatch, FullMatch, SpacePolicy
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

channel = Channel.current()


async def yangyang(uid):
    try:
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'Connection': 'keep-alive',
            'content-type': 'application/json',
            'Referer': 'https://servicewechat.com/wx141bfb9b73c970a9/16/page-frame.html',
            "t": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQzMDcyNDYsIm5iZiI6MTY2MzIwNTA0NiwiaWF0IjoxNjYzMjAzMjQ2LCJqdGkiOiJDTTpjYXRfbWF0Y2g6bHQxMjM0NTYiLCJvcGVuX2lkIjoiIiwidWlkIjo2Mjc4MzAwMCwiZGVidWciOiIiLCJsYW5nIjoiIn0.tQ6yoOcesvoJJNFyP5_cCoIWhd2wPf3VSlrIYN4XOO8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Mi 10 Lite Zoom Build/NZH54D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4313 MMWEBSDK/20220805 Mobile Safari/537.36 MMWEBID/2303 MicroMessenger/8.0.27.2220(0x28001B37) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android"
        }
        resp = requests.get(f"https://cat-match.easygame2021.com/sheep/v1/game/user_info?uid={uid}", headers=headers)
        if resp.status_code == 200 and 'wx_open_id' in resp.text:
            res = resp.json()
            openid = res['data']['wx_open_id']
            data = {
                "uuid": openid
            }
            resp = requests.post("https://cat-match.easygame2021.com/sheep/v1/user/login_tourist",
                                 data=json.dumps(data),
                                 headers=headers)
            token = json.loads(resp.text)["data"]["token"]
            link1 = "https://cat-match.easygame2021.com/sheep/v1/game/game_over?rank_score=1&rank_state=1&rank_time=150&rank_role=1&skin=1"
            link2 = "https://cat-match.easygame2021.com/sheep/v1/game/topic_game_over?rank_score=1&rank_state=1&rank_time=500&rank_role=2&skin=1"  # 每日挑战
            head = {
                "t": token,
                "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Mi 10 Lite Zoom Build/NZH54D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/4313 MMWEBSDK/20220805 Mobile Safari/537.36 MMWEBID/2303 MicroMessenger/8.0.27.2220(0x28001B37) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android"
            }
            requests.get(link1, headers=head)
            requests.get(link2, headers=head)
        else:
            return False
    except Exception as e:
        return "错误！请在小程序里点击俺的名片查看ID，重新发送‘羊了个羊 DI号’"
    return "羊成功了！"

@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[Twilight(
        [FullMatch("羊了个羊").space(SpacePolicy.PRESERVE),
         WildcardMatch() @ "yid"]
    )]
))
async def yang(app: Ariadne, group: Group, member: Member, yid: MatchResult):
    try:
        yid = str(yid.result)
        await app.sendMessage(group, MessageChain.create(At(member.id), f"\n", await yangyang(yid)))
    
    except:
        await app.sendMessage(group, MessageChain.create(At(member.id), f"\n错误！请在小程序里点击俺的名片查看ID，重新发送‘羊了个羊 DI号’"))


