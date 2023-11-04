import re
from datetime import datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchRegex
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   decorators=[
                       MatchRegex(
                           regex=r'财富排行榜|连签排行榜|签到排行榜|活跃排行榜|会员排行榜|咸鱼排行榜|大咸鱼排行榜|金色咸鱼排行榜|七彩大咸鱼排行榜',
                           flags=re.RegexFlag(re.I))]))
async def money_list(app: Ariadne, member: Member, group: Group, message: MessageChain):
    async def template(all_list, title, name, suffix):
        num_dict = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
        num_list = 1
        text = f'{title}\n'
        for data in all_list:
            try:
                qq_name = (await app.get_member(group, data[0])).name
            except:
                qq_name = '已退群'
            text += f'第{num_dict[num_list]}名：{qq_name}({data[0]})\n{name}：{data[1]}{suffix}\n\n'
            num_list += 1
        return text

    if await Sql.is_open(group.id):
        if str(message) == '财富排行榜':
            all_list = await Sql.get_moneylist(group.id, 'Money')
            text = await template(all_list, '💰财富排行榜💰', '财富总额', '蜜桃币')
            await app.send_message(group, text)
        elif str(message) == '连签排行榜':
            all_list = await Sql.get_moneylist(group.id, 'even_sign')
            text = await template(all_list, '⚔️连签排行榜⚔️', '连签天数', '天')
            await app.send_message(group, text)
        elif str(message) == '签到排行榜':
            all_list = await Sql.get_moneylist(group.id, 'total_sign')
            text = await template(all_list, '💥签到排行榜💥', '签到天数', '天')
            await app.send_message(group, text)
        elif str(message) == '活跃排行榜':
            all_list = await Sql.get_moneylist(group.id, 'say_num')
            text = await template(all_list, '💦活跃排行榜💦', '累计发言', '次')
            await app.send_message(group, text)
        elif str(message) == '会员排行榜':
            all_list = await Sql.get_moneylist(group.id, 'vip_time')
            vip_list = ()
            for i in all_list:
                vip_time = datetime.strftime(datetime.fromtimestamp(i[1]), '%Y-%m-%d %H:%M:%S')
                vip_list += ((i[0], vip_time),)
            text = await template(vip_list, '🏮会员排行榜🏮', '到期时间', '')
            await app.send_message(group, text)
        elif str(message) == '咸鱼排行榜':
            all_list = await Sql.get_fishlist(group.id, '4_fish')
            text = await template(all_list, '🐟咸鱼排行榜🐟', '咸鱼数量', '条')
            await app.send_message(group, text)
        elif str(message) == '大咸鱼排行榜':
            all_list = await Sql.get_fishlist(group.id, '3_fish')
            text = await template(all_list, '🐟大咸鱼排行榜🐟', '大咸鱼数量', '条')
            await app.send_message(group, text)
        elif str(message) == '金色咸鱼排行榜':
            all_list = await Sql.get_fishlist(group.id, '2_fish')
            text = await template(all_list, '🐟金色咸鱼排行榜🐟', '金色咸鱼数量', '条')
            await app.send_message(group, text)
        elif str(message) == '七彩大咸鱼排行榜':
            all_list = await Sql.get_fishlist(group.id, '1_fish')
            text = await template(all_list, '🐟七彩大咸鱼排行榜🐟', '七彩大咸鱼数量', '条')
            await app.send_message(group, text)
