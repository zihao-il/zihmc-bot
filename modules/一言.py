import random

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent, DetectPrefix
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from modules.mysql import Sql

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("一言")]))
async def a_word(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if await Sql.is_open(group.id):
        session = Ariadne.service.client_session
        async with session.get("https://v1.hitokoto.cn") as w:
            data = await w.json()
        if data["from_who"] == 'null' or data["from_who"] is None:
            await app.send_message(group, f'{data["hitokoto"]}\n  —{data["from"]}')
        else:
            await app.send_message(group, f'{data["hitokoto"]}\n  —{data["from"]} {data["from_who"]}')


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("今天吃什么")]))
async def what_eat(app: Ariadne, group: Group, member: Member):
    if await Sql.is_open(group.id, 'is_lot'):
        eats = ['华莱士', '塔斯汀', '竹笋烤肉', '盖浇饭', '砂锅', '大排档', '米线', '西餐', '自助餐', '炒面',
                '快餐', '水果', '西北风', '馄饨', '火锅', '烧烤', '泡面', '水饺', '日本料理', '涮羊肉', '味千拉面',
                '面包', '扬州炒饭', '自助餐', '菜饭骨头汤', '茶餐厅', '海底捞', '披萨', '麦当劳', 'KFC',
                '汉堡王', '兰州拉面', '沙县小吃', '烤鱼', '烤肉', '海鲜', '铁板烧', '韩国料理', '粥', '快餐',
                '萨莉亚', '桂林米粉', '东南亚菜', '甜点', '农家菜', '鲁菜', '川菜', '粤菜', '湘菜', '本帮菜', '酸辣粉',
                '螺蛳粉', '黄焖鸡米饭', '泡面', '馋嘴鱼', '干锅', '便当', '煲仔饭', '汤粉', '炸鸡汉堡', '烧腊饭',
                '烧烤', '麻辣烫', '豚骨拉面', '水煮鱼', '热松饼', '臭豆腐', '蜜汁叉烧', '汤圆', '蘑菇肉片',
                '猪肉炖粉条', '红烧鲈鱼', '酸菜鱼', '三明治', '红烧排骨', '红饶肉', '肉夹馍', '鸡蛋灌饼', '凉皮',
                '凉面',
                '酸辣粉', '红烧牛肉面', '鲜虾鱼板面', '老坛酸菜牛肉面', '藤椒牛肉面', '香菇炖鸡面', '粉面菜蛋',
                '西红柿炒鸡蛋', '冒菜', '麻婆豆腐', '自热火锅']
        eta = random.choice(eats)
        await app.send_message(group, eta)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("今天喝什么")]))
async def what_drink(app: Ariadne, group: Group, member: Member):
    if await Sql.is_open(group.id, 'is_lot'):
        drinks = ['柠檬水', '棒打鲜橙', '芝士奶盖四季春', '菠萝爱情海', '菠萝甜心橙', '桃喜芒芒', '百香芒芒',
                  '棒打鲜橙', '芋圆葡萄', '菠萝甜心橙', '柠檬红茶', '柠檬绿茶', '满杯百香果', '蜜桃四季春', '黄桃果霸',
                  '珍珠奶茶', '椰果奶茶', '布丁奶茶', '美式咖啡', '拿铁咖啡', '芝士奶盖红茶', '芝士奶盖绿茶']
        drink = random.choice(drinks)
        await app.send_message(group, drink)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[DetectPrefix("随机")], ))
async def compute(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("随机")):
    if await Sql.is_open(group.id, 'is_lot'):
        try:
            await app.send_message(group, random.choice(str(message).split(' ')))
        except:
            return
