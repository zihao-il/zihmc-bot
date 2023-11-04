import re
from datetime import datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([RegexMatch(r'epic周免').flags(re.I)])], ))
async def get_epic(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):

        session = Ariadne.service.client_session
        async with session.get(
                "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN") as t:
            json_data = await t.json()
        for i in json_data['data']['Catalog']['searchStore']['elements']:
            name = i['title']
            imgurl = i['keyImages'][0]['url']
            if len(i["catalogNs"]["mappings"]) != 0:
                link = f'https://store.epicgames.com/zh-CN/p/{i["catalogNs"]["mappings"][0]["pageSlug"]}'
            else:
                link = '无'
                continue
            jiage = i['price']['totalPrice']['fmtPrice']['originalPrice']
            if i['promotions'] is not None:
                try:
                    starttime = i['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['startDate']
                    starttime = datetime.fromisoformat(starttime[:-1])

                except:
                    starttime = '未开始'
                    continue

                try:
                    endtime = i['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['endDate']
                    endtime = datetime.fromisoformat(endtime[:-1])

                except:
                    endtime = '未知'
                    continue
            await app.send_message(group, MessageChain(
                [Image(url=imgurl),
                 f'\n名字：{name}\n链接：{link}\n原价：{jiage}\n开始时间：{starttime}\n结束时间：{endtime}']))
