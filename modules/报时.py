from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Voice
from graia.saya import Channel
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler.timers import crontabify
from graiax import silkcoder

from modules.mysql import Sql

channel = Channel.current()


@channel.use(SchedulerSchema(crontabify("30 6 * * *")))
async def good_morning(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜早上好.wav")
    for g in (await Sql.select_open('qq_group', 'tell_time', 1)):
        await app.send_group_message(g[0], MessageChain(Voice(data_bytes=voice_bytes)))


@channel.use(SchedulerSchema(crontabify("0 12 * * *")))
async def good_noon(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜中午好.wav")
    for g in (await Sql.select_open('qq_group', 'tell_time', 1)):
        await app.send_group_message(g[0], MessageChain(Voice(data_bytes=voice_bytes)))


@channel.use(SchedulerSchema(crontabify("0 20 * * *")))
async def good_night(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜晚上好.wav")
    for g in (await Sql.select_open('qq_group', 'tell_time', 1)):
        await app.send_group_message(g[0], MessageChain(Voice(data_bytes=voice_bytes)))
