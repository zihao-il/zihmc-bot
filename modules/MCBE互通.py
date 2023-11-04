import asyncio
import base64
import hashlib
import json

import websockets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.model import Member
from graia.broadcast.interrupt import InterruptControl, Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import ListenerSchema

saya = Saya.current()

channel = Channel.current()
inc = InterruptControl(saya.broadcast)


@channel.use(ListenerSchema(listening_events=[GroupMessage], decorators=[MatchContent("开启互通")], ))
async def ws_mcserver(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if member.id != 1767927045:
        await app.send_message(group, '丑拒！无权！！！')
        return

    @Waiter.create_using_function([GroupMessage])
    async def group_msg(g: Group, event: GroupMessage):
        if group.id == g.id:
            return str(event.message_chain), event.sender.name

    url = "ws://127.0.0.1:19132/mcws"
    password = "password114514"

    async def aes_cbc_encrypt(text, pwd):
        md5 = hashlib.md5()
        md5.update(pwd.encode("utf-8"))
        password_md5 = md5.hexdigest().upper()
        key = password_md5[:16]
        iv = password_md5[16:]
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        padded_text = pad(text.encode('utf-8'), AES.block_size)
        encrypted_text = cipher.encrypt(padded_text)
        base64_encoded = base64.b64encode(encrypted_text).decode('utf-8')
        return base64_encoded

    async def send_message(websocket):
        while True:
            msg_qq = await inc.wait(group_msg)
            msg_data = f'【§eQQ群§f】 §b{msg_qq[1]}： §f{msg_qq[0]}'
            msg_qq_data = '{"type":"pack","action": "runcmdrequest","params": {"cmd": "tellraw @a {\\"rawtext\\":[{\\"text\\":\\"%s\\"}]}", "id": 0}}' % msg_data
            base64_data = await aes_cbc_encrypt(msg_qq_data, password)
            s_data = '{"type": "encrypted","params": {"mode": "aes_cbc_pck7padding","raw": "%s"}}' % base64_data
            await websocket.send(s_data)

    async def receive_message(websocket):
        while True:
            received_message = await websocket.recv()
            msg_json = json.loads(received_message)
            send_msgs = '【服务器】'
            if msg_json['cause'] == 'join':
                send_msgs += f"{msg_json['params']['sender']}  加入了服务器！"
            elif msg_json['cause'] == 'left':
                send_msgs += f"{msg_json['params']['sender']}  离开了服务器！"
            elif msg_json['cause'] == 'chat':
                send_msgs += f"{msg_json['params']['sender']}：{msg_json['params']['text']}"
            elif msg_json['cause'] == 'death':
                send_msgs += f"{msg_json['params']['msg']}"
            else:
                continue

            await app.send_message(group, send_msgs)

    async def connect_to_websocket():

        async with websockets.connect(url, extra_headers={"Authorization": password}) as websocket:
            await app.send_message(group, '连接服务器成功！')

            tasks = [
                asyncio.create_task(send_message(websocket)),
                asyncio.create_task(receive_message(websocket))
            ]

            await asyncio.gather(*tasks)

    try:
        await connect_to_websocket()
    except:
        await app.send_message(group, '服务器已关闭！')
        return
