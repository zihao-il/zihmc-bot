import json
import re

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.base import DetectSuffix, MatchContent
from graia.ariadne.model import Member, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler.timers import crontabify

from modules.mysql import Sql

channel = Channel.current()


async def forum_sign(name, link, cookie):
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12; 22081212C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
        'cookie': cookie
    }
    session = Ariadne.service.client_session
    try:
        async with session.get(url=link, headers=headers) as text:
            sign_text = await text.text()

    except:
        return f'{name}网址无法访问！'
    if sign_text == '':
        return f'{name}访问错误！'
    if bool(re.findall(r"您当前的访问请求当中含有非法字符，已经被系统拒绝", sign_text)):
        return f'cookie错误！请发送{name}更新cookie"cookie"'
    sign_text = re.findall(r'<root><!\[CDATA\[(.*)]]></root>', sign_text)
    return f"{name}签到状态：{sign_text[0]}"


async def animal_sign(appid, authorization):
    headers = {
        "Cache-Control": "no-cache",
        "AppID": appid,
        "Version": "3.3.4",
        "Authorization": authorization,
        "Host": "api1.mimikko.cn",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.12.1",
    }

    sign_link = "https://api1.mimikko.cn/client/RewardRuleInfo/SignAndSignInformationV3"
    exp_link = "https://api1.mimikko.cn/client/love/ExchangeReward?code=miruku2"

    session = Ariadne.service.client_session
    try:
        async with session.get(url=sign_link, headers=headers) as text:
            sign_day = await text.text()
        sign_json = json.loads(sign_day)
        if sign_json["code"] != "0":
            sign_msg = sign_json["msg"]
        else:
            sign_msg = [
                Plain(f'获得的好感度：{sign_json["body"]["Reward"]}\n'),
                Plain(f'{sign_json["body"]["Description"]}\n{sign_json["body"]["Name"]}\n'),
                Image(url=f'{sign_json["body"]["PictureUrl"]}'),
            ]
    except:
        sign_msg = f'兽耳网址无法访问!'

    try:
        async with session.get(url=exp_link, headers=headers) as text:
            exp_day = await text.text()
        exp_json = json.loads(exp_day)
        if exp_json["code"] != "0":
            exp_msg = exp_json["msg"]
        else:
            exp_msg = f'兑换成功：{exp_json["body"]["Favorability"]}/{exp_json["body"]["MaxFavorability"]}'
    except:
        exp_msg = f'兽耳网址无法访问!'

    return sign_msg, exp_msg


# @channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("自动签到")]))


@channel.use(SchedulerSchema(crontabify("5 6 * * *")))
async def auto_sign_time(app: Ariadne):
    mt_content = await Sql.get_signkey('mt')
    mt_cookie = mt_content[0][1]
    mt_formhash = mt_content[0][2]
    link = f'https://bbs.binmt.cc/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash={mt_formhash}'
    await app.send_group_message(196619774, await forum_sign('mt', link, mt_cookie), )

    yd_content = await Sql.get_signkey('阅读')
    yd_cookie = yd_content[0][1]
    yd_formhash = yd_content[0][2]
    link = f'https://legado.cn/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash={yd_formhash}'
    await app.send_group_message(196619774, await forum_sign('阅读', link, yd_cookie), )

    content = await Sql.get_signkey('兽耳')
    appid = content[0][1]
    authorization = content[0][2]
    await app.send_group_message(196619774, MessageChain((await animal_sign(appid, authorization))[0]), )
    await app.send_group_message(196619774, MessageChain((await animal_sign(appid, authorization))[1]), )


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectSuffix("重新签到")], ))
async def resign(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectSuffix("重新签到")):
    if await Sql.is_founder(member.id):
        if str(message).lower() == 'mt':
            content = await Sql.get_signkey('mt')
            cookie = content[0][1]
            formhash = content[0][2]
            link = f'https://bbs.binmt.cc/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash={formhash}'
            await app.send_message(group, await forum_sign('mt', link, cookie), )

        elif str(message) == '阅读':
            content = await Sql.get_signkey('阅读')
            cookie = content[0][1]
            formhash = content[0][2]
            link = f'https://legado.cn/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash={formhash}'
            await app.send_message(group, await forum_sign('阅读', link, cookie), )
        elif str(message) == '兽耳':
            content = await Sql.get_signkey('兽耳')
            appid = content[0][1]
            authorization = content[0][2]

            await app.send_message(group, MessageChain((await animal_sign(appid, authorization))[0]), )
            await app.send_message(group, MessageChain((await animal_sign(appid, authorization))[1]), )
