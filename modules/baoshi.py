from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Voice
from graia.saya import Channel
from graiax import silkcoder


channel = Channel.current()


@channel.use(SchedulerSchema(crontabify("30 6 * * *")))
async def goodMorning(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜早上好.wav")
    await app.sendGroupMessage(855150997, MessageChain.create(Voice(data_bytes=voice_bytes)))


@channel.use(SchedulerSchema(crontabify("0 12 * * *")))
async def goodNoon(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜中午好.wav")
    await app.sendGroupMessage(855150997, MessageChain.create(Voice(data_bytes=voice_bytes)))

@channel.use(SchedulerSchema(crontabify("0 20 * * *")))
async def goodNight(app: Ariadne):
    voice_bytes = await silkcoder.async_encode("data/姜晚上好.wav")
    await app.sendGroupMessage(855150997, MessageChain.create(Voice(data_bytes=voice_bytes)))

