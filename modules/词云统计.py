import csv
import datetime
from random import randint

import jieba
import numpy as np
from PIL import Image as IMG
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler.timers import crontabify
from wordcloud import WordCloud

from modules.mysql import Sql

channel = Channel.current()


async def create_cy(txt, _id):
    def random_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None,
                          random_state=None):
        h = randint(60, 300)
        s = int(100.0 * 255.0 / 255.0)
        l = int(100.0 * float(randint(30, 300)) / 255.0)
        return f"hsl({h}, {s}%, {l}%)"

    pho_name = 'data/词云背景图.png'
    c_ttf = r"C:\Users\Administrator\AppData\Local\Microsoft\Windows\Fonts\SourceHanSerifCN-SemiBold.otf"

    words = jieba.lcut(txt)
    txt = ''.join(words)
    try:
        mask = np.array(IMG.open(pho_name))
    except:
        image = IMG.new('RGB', (2048, 2048), (0, 0, 0))
        image.save(pho_name)
        mask = np.array(IMG.open(pho_name))

    wordcloud = WordCloud(
        background_color="black",
        width=2048,
        height=2048,
        max_words=300,
        min_font_size=10,
        max_font_size=120,
        color_func=random_color_func,
        mask=mask,
        contour_width=4,
        contour_color='white',
        font_path=c_ttf
    ).generate(txt)
    wordcloud.to_file(f'temp/词云图_{_id}.png')


@channel.use(
    ListenerSchema(listening_events=[GroupMessage], inline_dispatchers=[Twilight([RegexMatch(r'^(本周|上周)词云'), ])]))
async def group_cy(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        cy_id = str(message).split('词云')[0]
        today = datetime.datetime.now()
        await app.send_message(group, "正在统计中...")
        if cy_id == '本周':
            path = f"data/msg/{today.isocalendar()[0]}-{today.isocalendar()[1]}.csv"
        elif cy_id == '上周':
            path = f"data/msg/{today.isocalendar()[0]}-{today.isocalendar()[1] - 1}.csv"

        txt = ''
        with open(path, encoding="utf-8-sig", newline='') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[1] != str(group.id):
                    continue
                txt += (row[5] + '\n').replace('\'', "")
        try:
            await create_cy(txt, f"群{str(group.id)}")
        except:
            return await app.send_message(group, "无统计记录！")
        await app.send_message(group, Image(path=f'temp\词云图_群{group.id}.png'))


@channel.use(SchedulerSchema(crontabify("30 8 * * 1")))
async def event_cy(app: Ariadne):
    today = datetime.datetime.now()
    path = f"data/msg/{today.isocalendar()[0]}-{today.isocalendar()[1] - 1}.csv"
    for g in [933238308, 855150997, 1091061241]:
        txt = ''
        with open(path, encoding="utf-8-sig", newline='') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                if row[1] != str(g):
                    continue
                txt += (row[5] + '\n').replace('\'', "")
        try:
            await create_cy(txt, f"群{str(g)}")
        except:
            return await app.send_group_message(g, "无统计记录！")
        await app.send_group_message(g, ['上周群词云统计！\n', Image(path=f'temp\词云图_群{g}.png')])
