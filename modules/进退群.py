from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import MemberLeaveEventQuit, MemberJoinEvent, NewFriendRequestEvent, \
    BotInvitedJoinGroupRequestEvent, MemberJoinRequestEvent
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

from modules.imgHandle import ImgHandle
from modules.mysql import Sql

saya = Saya.current()

channel = Channel.current()
inc = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[MemberLeaveEventQuit]))
async def leave_group(app: Ariadne, event: MemberLeaveEventQuit, group: Group, member: Member):
    if await Sql.is_open(group.id):
        bad_img = await ImgHandle.get_badimg(await member.get_avatar(640))
        leave_text = await Sql.select_open('leave_message', 'qq_group', group.id)
        await Sql.add_blacklist(group.id, member.id)

        if len(leave_text) == 0 or leave_text[0][0] is None or leave_text[0][0] == '':
            leave_text = '退出了本群！'
        else:
            leave_text = leave_text[0][0]
        await app.send_message(group, MessageChain(
            [Image(data_bytes=bad_img), Plain(f"\n退群通知：\n{member.name}({member.id})\n{leave_text}")]), )


# @channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("加群")]))
@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def join_group(app: Ariadne, group: Group, event: MemberJoinEvent, member: Member):
    if await Sql.is_open(group.id):
        if await Sql.is_open(group.id, 'is_blacklist'):  # 开启黑名单
            if len(await Sql.get_blacklist(group.id, member.id)) != 0:
                await app.send_message(group, MessageChain([Plain(f"发现黑名单用户，即将踢出！！！")]), )
                await app.kick_member(group.id, member.id, '黑名单用户，禁止二次入群')
                return
        join_text = await Sql.select_open('add_message', 'qq_group', group.id)
        if len(join_text) == 0 or join_text[0][0] is None or join_text[0][0] == '':
            join_text = '加入了本群！'
        else:
            join_text = join_text[0][0]
        await app.mute_member(group.id, member.id, (await Sql.select_open('join_mute', 'qq_group', group.id))[0][0])
        await app.send_message(group, MessageChain(
            [Image(data_bytes=await member.get_avatar(640)),
             Plain(f"\n入群通知：\n{member.name}({member.id})\n{join_text}")]), )
        await Sql.add_qq(group.id, member.id)

        @Waiter.create_using_function([GroupMessage])
        async def group_send(g: Group, m: Member, msg: MessageChain):
            if group.id == g.id and member.id == m.id:
                return msg

        get_timeout = await Sql.select_open('time_out_kick', "qq_group", group.id)
        if int(get_timeout[0][0]) == 0:
            await Sql.add_qq(group.id, member.id)
            return
        else:
            try:
                await inc.wait(group_send, timeout=get_timeout[0][0])
                await Sql.add_qq(group.id, member.id)
            except:
                await app.kick_member(group.id, member.id, '进群未发言，已被踢出！')


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def add_bot_friend(app: Ariadne, event: NewFriendRequestEvent):
    await app.send_friend_message(1767927045,
                                  f'有新人加我好友\n申请人：{event.nickname}({event.supplicant})\n申请消息：{event.message}\n来源：{event.source_group}')
    await event.accept()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def add_bot_group(app: Ariadne, event: BotInvitedJoinGroupRequestEvent):
    await app.send_friend_message(1767927045,
                                  f'有人拉我进群\n群名称：{event.group_name}({event.source_group})\n申请消息：{event.message}\n邀请人：{event.nickname}({event.supplicant})')
    await event.reject('请征求主人的同意！')


@channel.use(ListenerSchema(listening_events=[MemberJoinRequestEvent]))
async def accept_add_group(app: Ariadne, event: MemberJoinRequestEvent):
    if await Sql.is_open(event.source_group):
        await event.accept()
