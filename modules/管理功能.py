import re

from graia.amnesia.message.formatter import Formatter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Face
from graia.ariadne.message.formatter import Formatter
from graia.ariadne.message.parser.base import MatchRegex, DetectPrefix
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, ElementMatch, RegexMatch, MatchResult, \
    WildcardMatch
from graia.ariadne.model import Group, Friend
from graia.ariadne.model import Member
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()
saya = Saya.current()


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('奖励'), "at" @ ElementMatch(At), 'money' @ RegexMatch(r"\d+")])], ))
async def add_coin(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult,
                   money: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            await Sql.change_money(group.id, str(at.result)[1:], 'Money', money.result, '+')
            await app.send_message(group,
                                   Formatter("恭喜{a}获得{m}蜜桃币").format(a=at.result, m=money.result), )
        else:
            await app.send_message(group, '丑拒，权限不足！')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('扣除'), "at" @ ElementMatch(At), 'money' @ RegexMatch(r"\d+")])], ))
async def remove_coin(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult,
                      money: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            await Sql.change_money(group.id, str(at.result)[1:], 'Money', money.result, '-')
            await app.send_message(group,
                                   Formatter("{a}受到惩罚，扣除{m}蜜桃币").format(a=at.result, m=money.result), )
        else:
            await app.send_message(group, '丑拒，权限不足！')


@channel.use(ListenerSchema(listening_events=[GroupMessage],
                            decorators=[MatchRegex(regex=r'开启全员禁言|关闭全员禁言', )]))
async def all_mute(app: Ariadne, member: Member, group: Group, message: MessageChain):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            if str(message) == '开启全员禁言':
                await app.mute_all(group)
            elif str(message) == '关闭全员禁言':
                await app.unmute_all(group)


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('禁言'), "at" @ ElementMatch(At), 'mute_time' @ WildcardMatch()])], ))
async def mute(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult,
               mute_time: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 1:
            at_qq = int(str(at.result)[1:])
            qq_name = (await app.get_member(group, at_qq)).name
            if await Sql.get_group_field('purview', group.id, at_qq) >= 1:
                return await app.send_message(group, Formatter(
                    '【{qq_name}】({at_qq})是机器人的管理员，{at}你不能禁言他!').format(
                    qq_name=qq_name,
                    at_qq=at_qq,
                    at=At(member.id), ), )

            if str(mute_time.result) == '':

                try:
                    await app.mute_member(group.id, at_qq, 600)
                except:
                    pass
                return await app.send_message(group, Formatter('{at} 已被禁言十分钟').format(at=At(at_qq)))
            else:
                async def get_time(g):
                    if len(g) == 0:
                        gt = '0'
                    else:
                        gt = g[0]
                    return gt

                day_time = await get_time(re.compile(r'(\d+)天').findall(str(mute_time.result)))
                hour_time = await get_time(re.compile(r'(\d+)小时').findall(str(mute_time.result)))
                minute_time = await get_time(re.compile(r'(\d+)分钟').findall(str(mute_time.result)))
                if day_time == '0' and hour_time == '0' and minute_time == '0':
                    return
                m_time = int(day_time) * 86400 + int(hour_time) * 3600 + int(minute_time) * 60
                day = int(m_time / 86400)
                hour = int(m_time % 86400 / 3600)
                minute = int(m_time % 86400 % 3600 / 60)
                c_mute_time = f'{f"{day}天" if day else ""}{f"{hour}小时" if hour else ""}{f"{minute}分钟" if minute else ""}'
                try:
                    await app.mute_member(group.id, at_qq, m_time)
                except:
                    pass
                return await app.send_message(group, Formatter('{at} 已被禁言{t}').format(at=At(at_qq),
                                                                                          t=c_mute_time))
        else:
            return await app.send_message(group, '只有机器人的管理员才能执行禁言或解除禁言操作')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('解除禁言'), "at" @ ElementMatch(At)])], ))
async def un_mute(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 1:
            at_qq = int(str(at.result)[1:])
            await app.unmute_member(group.id, at_qq)
            return await app.send_message(group, Formatter(
                '【{at_qq}】被{at}解除禁言').format(
                at_qq=At(at_qq),
                at=At(member.id), ), )
        else:
            return await app.send_message(group, '只有机器人的管理员才能执行禁言或解除禁言操作')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('添加管理员'), "at" @ ElementMatch(At)])], ))
async def add_admin(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            at_qq = int(str(at.result)[1:])
            await Sql.set_money(group.id, at_qq, 'purview', 1)
            return await app.send_message(group, Formatter('{face}祝贺新群管{at}').format(face=Face(144), at=At(at_qq)))
        else:
            return await app.send_message(group, '丑拒，权限不足')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('删除管理员'), "at" @ ElementMatch(At)])], ))
async def remove_admin(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            at_qq = int(str(at.result)[1:])
            await Sql.set_money(group.id, at_qq, 'purview', 0)
            return await app.send_message(group, Formatter('已删除机器人管理员{at}').format(at=At(at_qq)))
        else:
            return await app.send_message(group, '丑拒，权限不足')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('更新成员列表')])], ))
async def member_list(app: Ariadne, member: Member, group: Group, message: MessageChain, ):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            m_list = await app.get_member_list(group.id)
            for i in m_list:
                await Sql.add_qq(group.id, i.id)


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight(["at" @ ElementMatch(At), FullMatch('撤回')])], decorators=[], ))
async def recall_message(app: Ariadne, member: Member, group: Group, message: MessageChain, at: MatchResult,
                         event: GroupMessage):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 1:
            msg = await app.get_message_from_id(event.quote.id, group)
            try:
                await app.recall_message(msg, group)
            except:
                return app.send_message(group, '撤回消息失败！')
            await app.send_message(group, '成功撤回一条消息！')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('拉黑'), "at" @ ElementMatch(At, optional=True),
                                 "qq" @ RegexMatch(r'\d+', optional=True)])], ))
async def add_black_list(app: Ariadne, group: Group, member: Member, message: MessageChain, at: MatchResult,
                         qq: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            if at.result is None and qq.result is None:
                return
            if at.result is not None:
                qq_member = int(str(at.result)[1:])
            elif qq.result is not None:
                qq_member = int(str(qq.result))
            else:
                return app.send_message(group, '拉黑失败！')

            await Sql.add_blacklist(group.id, qq_member)
            await app.send_message(group, f'{qq_member}已被拉黑，下次他将无法自动加进群！')

        else:
            return await app.send_message(group, '丑拒，权限不足')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('解除拉黑'), "qq" @ RegexMatch(r'\d+')])], ))
async def del_black_list(app: Ariadne, group: Group, member: Member, message: MessageChain, qq: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            qq_member = int(str(qq.result))

            await Sql.del_blacklist(group.id, qq_member)
            await app.send_message(group, f'{qq_member}已被解除拉黑。')

        else:
            return await app.send_message(group, '丑拒，权限不足')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage],
                   inline_dispatchers=[
                       Twilight([FullMatch('踢黑'), "at" @ ElementMatch(At, optional=True),
                                 "qq" @ RegexMatch(r'\d+', optional=True)])], ))
async def kick_black_list(app: Ariadne, group: Group, member: Member, message: MessageChain, at: MatchResult,
                          qq: MatchResult):
    if await Sql.is_open(group.id):
        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            if at.result is None and qq.result is None:
                return
            if at.result is not None:
                qq_member = int(str(at.result)[1:])
            elif qq.result is not None:
                qq_member = int(str(qq.result))
            else:
                return app.send_message(group, '踢黑失败！')
            qq_name = (await app.get_member(group, qq_member)).name
            await Sql.add_blacklist(group.id, qq_member)
            await app.kick_member(group.id, qq_member, '违反群规已被踢出并拉黑！')
            await app.send_message(group, f'{qq_name}({qq_member})赢得了一张免费机票，大家欢送他起飞～')

        else:
            return await app.send_message(group, '丑拒，权限不足')


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def bot_message(app: Ariadne, event: FriendMessage, friend: Friend):
    if int(event.sender) == 1767927045 or int(event.sender) == app.default_account:
        return
    await app.send_friend_message(1767927045, f"发送者：{event.sender}\n内容：\n{event.message_chain}")


@channel.use(ListenerSchema(listening_events=[FriendMessage], inline_dispatchers=[
    Twilight([FullMatch('回复'), "qq" @ RegexMatch(r'\d+'), 'content' @ WildcardMatch()])], ))
async def bot_message(app: Ariadne, event: FriendMessage, friend: Friend, qq: MatchResult, content: MatchResult, ):
    if int(event.sender) != 1767927045:
        return
    await app.send_friend_message(int(str(qq.result)), f"{str(content.result)}")


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("添加违禁词")], ))
async def add_ban_word(app: Ariadne, member: Member, group: Group, message: MessageChain = DetectPrefix('添加违禁词')):
    if await Sql.is_open(group.id):

        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            _ban_word = (await Sql.select_open("ban_word", "qq_group", group.id))[0][0]
            ban_word_list = _ban_word.split("|")
            ban_word_list.append(str(message))
            ban_word_list_join = '|'.join(ban_word_list)
            await Sql.change_group(group.id, "ban_word", ban_word_list_join)
            await app.send_message(group, '违禁词添加成功！')


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("删除违禁词")], ))
async def remove_ban_word(app: Ariadne, member: Member, group: Group,
                          message: MessageChain = DetectPrefix('删除违禁词')):
    if await Sql.is_open(group.id):

        if await Sql.get_group_field('purview', group.id, member.id) >= 2:
            _ban_word = (await Sql.select_open("ban_word", "qq_group", group.id))[0][0]
            ban_word_list = _ban_word.split("|")
            try:
                ban_word_list.remove(str(message))
            except:
                return await app.send_message(group, '没有此违禁词！')
            ban_word_list_join = '|'.join(ban_word_list)
            await Sql.change_group(group.id, "ban_word", ban_word_list_join)
            await app.send_message(group, '违禁词删除成功！')


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("重载模块")]))
async def reload(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix('重载模块')):
    if await Sql.is_founder(member.id):
        channel_path = str(message)
        if not (_channel := saya.channels.get(channel_path)):
            return await app.send_message(group, "该模组未安装, 您可能需要安装它")
        try:
            saya.reload_channel(_channel)
        except Exception as e:
            await app.send_message(group, f"重载 {channel_path} 失败！")
            raise e
        else:
            return await app.send_message(group, f"重载 {channel_path} 成功")
