from io import BytesIO
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent
from graia.saya.builtins.broadcast import ListenerSchema
from PIL import Image as IMG
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Image

def getheibaiimg(avatar: bytes) -> bytes:
    img = IMG.open(BytesIO(avatar))
    img = img.convert("L")
    imgbio = BytesIO()
    img.save(imgbio, "JPEG")
    return imgbio.getvalue()


channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("获取黑白头像")]))
async def heibaiimg(app: Ariadne, member: Member, group: Group):
    imgbt=getheibaiimg(await member.getAvatar(640))

    await app.sendMessage(
        group,
        MessageChain.create(
            At(member.id),
            Image(data_bytes=imgbt),
        ),
    )