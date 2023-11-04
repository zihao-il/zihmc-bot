import random
from datetime import datetime, timedelta

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At, Image, Face
from graia.ariadne.message.formatter import Formatter
from graia.ariadne.message.parser.base import MatchContent, MatchRegex
from graia.ariadne.message.parser.twilight import ElementMatch, Twilight, RegexResult, FullMatch
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.imgHandle import ImgHandle
from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchRegex(regex=r'签到|一键签到')]))
async def sign(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        try:
            await Sql.get_group_field('sign_time', group.id, member.id)
        except:
            await Sql.add_qq(group.id, member.id)

        sign_time = await Sql.get_group_field('sign_time', group.id, member.id)
        now_time = datetime.now().strftime('%Y-%m-%d')
        is_vip = await Sql.is_vip(group.id, member.id)
        if str(sign_time) != now_time:
            if (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') == str(sign_time):
                await Sql.change_money(group.id, member.id, 'even_sign', 1, '+')  # 连签+1
            else:
                await Sql.update_group_field('even_sign', 0, group.id, member.id)  # 重置连签

            await Sql.update_group_field('sign_time', now_time, group.id, member.id)  # 设置签到日期
            await Sql.change_money(group.id, member.id, 'total_sign', 1, '+')  # 设置总签到天数
            total_sign_day = await Sql.get_group_field('total_sign', group.id, member.id)
            if is_vip:
                money = random.randint(800, 1200)
                await Sql.change_money(group.id, member.id, 'Money', money, '+')
                await app.send_message(group,
                                       Formatter(
                                           "{img}\n{f1}签到者：{name}\n{f2}获得：{m}蜜桃币\n{f3}连续签到：{td}天").format(
                                           img=Image(path='data/签到成功-vip.png'), f1=Face(324), name=member.name,
                                           f2=Face(295), m=money, f3=Face(74), td=total_sign_day), )

            else:
                money = random.randint(300, 500)
                await Sql.change_money(group.id, member.id, 'Money', money, '+')
                await app.send_message(group,
                                       Formatter(
                                           "{img}\n{f1}签到者：{name}\n{f2}获得：{m}蜜桃币\n{f3}连续签到：{td}天").format(
                                           img=Image(path='data/签到成功.png'), f1=Face(324), name=member.name,
                                           f2=Face(295), m=money, f3=Face(74), td=total_sign_day), )

        else:
            remove_money = random.randint(100, 200)
            if is_vip:
                try:
                    await app.send_message(group,
                                           Formatter(
                                               "{img}\n{f1}签到者：{name}\n{f2}一天只能签到一次哦!*(^o^)/\n{f3}惩罚禁言3分钟并扣除{m}蜜桃币").format(
                                               img=Image(path='data/签到失败-vip.png'), f1=Face(324), name=member.name,
                                               f2=Face(22), f3=Face(7), m=remove_money), )
                    await Sql.change_money(group.id, member.id, 'Money', remove_money, '-')
                    await app.mute_member(group.id, member.id, 180)
                except:
                    pass
            else:
                try:
                    await app.send_message(group,
                                           Formatter(
                                               "{img}\n{f1}签到者：{name}\n{f2}一天只能签到一次哦!*(^o^)/\n{f3}惩罚禁言5分钟并扣除{m}蜜桃币").format(
                                               img=Image(path='data/签到失败.png'), f1=Face(324), name=member.name,
                                               f2=Face(22), f3=Face(7), m=remove_money), )
                    await Sql.change_money(group.id, member.id, 'Money', remove_money, '-')
                    await app.mute_member(group.id, member.id, 300)
                except:
                    pass


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("钱包")]))
async def wallet(app: Ariadne, member: Member, group: Group):
    if await Sql.is_open(group.id):
        try:
            await Sql.get_group_field('Money', group.id, member.id)
        except:
            await Sql.add_qq(group.id, member.id)

        money = await Sql.get_group_field('Money', group.id, member.id)
        await app.send_message(group, MessageChain([At(member.id), Plain(f"\n你拥有{money}蜜桃币")]), )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(FullMatch("积分"), "at" @ ElementMatch(At, optional=True), ), ]))
async def integral(app: Ariadne, member: Member, group: Group, at: RegexResult):
    if await Sql.is_open(group.id):
        if at.result is None:
            qq = member.id
        else:
            if await Sql.get_group_field('Money', group.id, member.id) < 100:
                return await app.send_message(group,
                                              MessageChain(
                                                  [At(member.id), Plain(f"\n蜜桃币不足！\n每次查询需要100蜜桃币")]), )
            else:
                await Sql.change_money(group.id, member.id, 'Money', 100, '-')
            qq = int(str(at.result)[1:])
        async with Ariadne.service.client_session.get(
                f"https://q2.qlogo.cn/headimg_dl?dst_uin={qq}&spec=640"
        ) as resp:
            qq_img = await resp.read()
        r_money = await Sql.get_ranking(group.id, qq, 'Money')
        money = await Sql.get_group_field('Money', group.id, qq)
        even = await Sql.get_group_field('even_sign', group.id, qq)
        r_even = await Sql.get_ranking(group.id, qq, 'even_sign')
        total = await Sql.get_group_field('total_sign', group.id, qq)
        r_total = await Sql.get_ranking(group.id, qq, 'total_sign')
        treasure = await Sql.get_group_field('treasure_data', group.id, qq)
        if treasure is None:
            treasure = ''
        else:
            treasure = "+".join(treasure.split('|'))
        await app.send_message(group,
                               MessageChain([At(member.id), Image(data_bytes=qq_img), Plain(
                                   f"\n🏆当前排名第{r_money[0][0]}位\n💰财富总额：{money}蜜桃币\n🔥连续签到：{even}天\n💫连续签到排名：第{r_even[0][0]}名\n👑总签到：{total}天\n🎈总签到排名：第{r_total[0][0]}名\n📦宝物列表：{treasure}")]), )


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("个人信息")]))
async def member_info(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        info_data = await member.get_profile()
        join_time = datetime.strftime(datetime.fromtimestamp(member.join_timestamp), '%Y年%m月%d日 %H点%M分%S秒')
        purview = int(await Sql.get_group_field('purview', group.id, member.id))
        if purview == 0:
            purview = '群员'
        elif purview == 1:
            purview = '管理员'
        elif purview >= 2:
            purview = '主人'
        special_title = member.special_title  # 头衔
        permission = str(member.permission)  # 群权限
        if permission == 'MEMBER':
            permission = "普通成员"
        elif permission == "ADMINISTRATOR":
            permission = '管理员'
        elif permission == "OWNER":
            permission = '群主'
        name = member.name  # 本群名称
        nickname = info_data.nickname
        email = info_data.email
        age = info_data.age
        level = info_data.level
        sign = info_data.sign  # 个性签名
        sex = str(info_data.sex)
        if sex == 'MALE':
            sex = "男性"
        elif sex == "FEMALE":
            sex = '女性'
        elif sex == "UNKNOWN":
            sex = '未知'
        await app.send_message(group, MessageChain(
            [Image(data_bytes=await member.get_avatar(640)),
             Plain(
                 f"\nQQ号：{member.id}\n昵称：{nickname}\n性别：{sex}\n年龄：{age}岁\n等级：{level}级\n头衔：{special_title}\n群名称：{name}\n群权限：{permission}\nBot权限：{purview}\n电子邮箱：{email}\n个性签名：{sign}\n加群时间：{join_time}")]), )


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("获取黑白头像")]))
async def grab_a_red_envelope(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        bad_img = await ImgHandle.get_badimg(await member.get_avatar(640))
        await app.send_message(group, MessageChain(
            [At(member.id), Image(data_bytes=bad_img)]), )
