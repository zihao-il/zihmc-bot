import random

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectSuffix
from graia.ariadne.message.parser.twilight import MatchResult, FullMatch, ParamMatch, RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


async def win_odds(win_num, qq_list):
    if len(qq_list) == 0:
        win_rate = "0.00%"
    elif int(win_num) >= len(qq_list):
        win_rate = "100.00%"
    else:
        win_f = (int(win_num) / len(qq_list[:-1])) * 100
        win_rate = "{:.2f}%".format(win_f)
    return win_rate


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[
        Twilight([FullMatch('发起抽奖'), 'title' @ ParamMatch(), 'win_num' @ RegexMatch(r'\d+'), FullMatch('人'),
                  'content' @ ParamMatch(), ])]
))
async def add_draw(app: Ariadne, member: Member, group: Group, message: MessageChain, title: MatchResult,
                   win_num: MatchResult,
                   content: MatchResult):
    win_num = int(str(win_num.result))
    if win_num <= 0:
        await app.send_message(group, "中奖人数不能小于等于0！")
        return
    title = str(title.result)
    content = str(content.result)
    try:
        await Sql.add_draw(member.id, win_num, title, content)
    except:
        return await app.send_message(group, "发起抽奖失败！")
    await app.send_message(group,
                           f"发起抽奖成功！\n发起人：{member.name}({member.id})\n奖品：{title}\n奖品简介：{content}\n中奖人数：{win_num}\n发送'参加{title}抽奖'参与抽奖！")


@channel.use(ListenerSchema(
    listening_events=[GroupMessage],
    inline_dispatchers=[
        Twilight([RegexMatch(r'参加|参与'), 'title' @ ParamMatch(), FullMatch('抽奖'),
                  ])]
))
async def join_draw(app: Ariadne, member: Member, group: Group, message: MessageChain, title: MatchResult):
    title = str(title.result)
    draw_info = await Sql.get_draw(title)
    if len(draw_info) == 0:
        return await app.send_message(group, "该抽奖不存在！")
    else:
        try:
            qq_list = (draw_info[0][3]).split('|')
        except:
            qq_list = ["10000"]
            pass
        if str(member.id) not in qq_list:
            if int(draw_info[0][4]) > len(qq_list):
                win_rate = "100.00%"
            else:
                win_f = (int(draw_info[0][4]) / len(qq_list)) * 100
                win_rate = "{:.2f}%".format(win_f)
            await Sql.join_draw(member.id, title)
            await app.send_message(group, MessageChain(
                [At(member.id), Plain("\n"),
                 f"参加{title}抽奖成功！\n你是当前第{len(qq_list)}个参与者\n中奖概率为{win_rate}"]), )
        else:
            await app.send_message(group, "你已经参与过该抽奖了！")


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectSuffix("抽奖信息")], ))
async def draw_info(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectSuffix("抽奖信息")):
    title = str(message)
    draw_info = await Sql.get_draw(title)
    if len(draw_info) == 0:
        return await app.send_message(group, "该抽奖不存在！")
    else:
        try:
            qq_list = (draw_info[0][3]).split('|')
        except:
            qq_list = []
            pass

        win_rate = await win_odds(draw_info[0][4], qq_list)
        await app.send_message(group, MessageChain([Plain(
            f"{title}的抽奖信息如下：\n发起人：{draw_info[0][0]}\n奖品：{draw_info[0][1]}\n奖品简介：{draw_info[0][2]}\n中奖人数：{draw_info[0][4]}\n参与人数：{len(qq_list) - 1}\n中奖概率：{win_rate}")]))


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectSuffix("开奖")], ))
async def open_draw(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectSuffix("开奖")):
    title = str(message)
    draw_info = await Sql.get_draw(title)
    if len(draw_info) == 0:
        return await app.send_message(group, "该抽奖不存在！")
    else:
        if str(member.id) == draw_info[0][0]:
            try:
                qq_list = (draw_info[0][3]).split('|')
            except:
                qq_list = []
            pass
            win_num = int(draw_info[0][4])
            win_qq = []
            if len(qq_list) == 0:
                await app.send_message(group, '没有人参与此抽奖！')
            elif len(qq_list) >= win_num:
                random_win = random.sample(qq_list[:-1], win_num)
                for i in random_win:
                    try:
                        await app.send_friend_message(int(i), f"恭喜你中奖₍˄·͈༝·͈˄*₎◞ ̑̑了！\n奖品为：{draw_info[0][1]}")
                    except:
                        pass
                    win_qq.append(i)
            else:
                for i in qq_list[:-1]:
                    try:
                        await app.send_friend_message(int(i), f"恭喜你中奖₍˄·͈༝·͈˄*₎◞ ̑̑了！\n奖品为：{draw_info[0][1]}")
                    except:
                        pass
                    win_qq.append(i)
            result = "\n".join(map(str, win_qq))
            win = "|".join(map(str, win_qq))
            win_rate = await win_odds(draw_info[0][4], qq_list)
            await app.send_message(group, f"中奖名单为：\n{result}\n中奖率为：{win_rate}")
            await Sql.close_draw(title, win)

        else:
            return await app.send_message(group, "只有发起人才能开奖！")


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectSuffix("中奖查询")], ))
async def open_draw(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectSuffix("中奖查询")):
    title = str(message)
    draw_info = await Sql.search_draw(title)
    win_qq = draw_info[0][5]
    if len(draw_info) == 0:
        return await app.send_message(group, "没有此抽奖！")
    if win_qq is None:
        await app.send_message(group, "没有人中奖！")
    else:
        try:
            qq_list = (draw_info[0][3]).split('|')
        except:
            qq_list = []
        pass
        win_num = "\n".join(win_qq.split("|"))
        win_rate = await win_odds(draw_info[0][4], qq_list)
        await app.send_message(group, f'{title}抽奖的中奖名单为：\n{win_num}\n中奖率为：{win_rate}')
