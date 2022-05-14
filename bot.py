from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import MemberLeaveEventQuit
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, MiraiSession, Member
from graia.scheduler import GraiaScheduler
import pkgutil
from pathlib import Path
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler.saya import GraiaSchedulerBehaviour
from graia.ariadne.message.element import Forward, ForwardNode, Image

app = Ariadne(
    MiraiSession(
        host="http://localhost:8060",  # 同 MAH 的 port
        verify_key="zzzzzz",  # 同 MAH 配置的 verifyKey
        account=3314535510,  # 机器人 QQ 账号
    ),
)
saya = app.create(Saya)

app.create(GraiaScheduler)

saya.install_behaviours(
    app.create(BroadcastBehaviour),
    app.create(GraiaSchedulerBehaviour),
)


with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        saya.require("modules." + module_info.name)

bcc = app.broadcast

@bcc.receiver("MemberLeaveEventQuit")
async def tuiqun(app: Ariadne, group: Group, message: MemberLeaveEventQuit):
    if group == 812057174:
        return
    await app.sendMessage(
        group,
        MessageChain.create(f'退群通知：\n@{message.member.name}({message.member.id})\n退出了本群！'),
    )

@bcc.receiver(GroupMessage)
async def setu(app: Ariadne, group: Group, message: MessageChain):
    # if str(message) == "你好":
    #     await app.sendMessag=
    #         group,
    #         MessageChain.create(f"不要说{message.asDisplay()}，来点涩图"),
    #     )

    if str(message) == "周年皮肤包":
        await app.sendMessage(
            group,
            MessageChain.create(f"周年皮肤包链接：https://zihao-il.github.io/index2.html"),
        )
    if str(message) == "鼻涕的肯定":
        await app.sendMessage(
            group,
            MessageChain.create(Image(path=Path("data/鼻涕的肯定.jpg"))),
        )

app.launch_blocking()

