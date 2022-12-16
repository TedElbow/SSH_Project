import asyncio
import socket
import threading

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import os.path

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100




async def main():
    global chat_msgs

    put_markdown("## 🧊 Welcome to Chat")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Enter Your Name", required=True, placeholder="Your name",
                           validate=lambda n: "That name has been used" if n in online_users or n == '📢' else None)
    online_users.add(nickname)
    privatekey = RSA.generate(2048)
    f = open("D:\SSI project\\TXT_For_Chat\\" + nickname + "privatekey.txt", "wb")
    f.write(bytes(privatekey.exportKey('PEM')))
    f.close()
    publickey = privatekey.publickey()
    f = open("D:\SSI project\\TXT_For_Chat\\" + nickname + "publickey.txt", 'wb')
    f.write(bytes(publickey.exportKey('PEM')))
    f.close()

    chat_msgs.append(('📢', f'`{nickname}` Connect to chat!'))
    msg_box.append(put_markdown(f'📢 `{nickname}` Connect to chat'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 New message", [
            input(placeholder="Text ...", name="msg"),
            actions(name="cmd", buttons=["Sent", {'label': "Exit", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "Enter the text of the message!") if m["cmd"] == "Sent" and not m['msg'] else None)
        plaintext = data['msg'].encode('utf-8')
        privatekey = RSA.importKey(open("D:\SSI project\\TXT_For_Chat\\" + nickname + "privatekey.txt",'rb').read())
        myhash = SHA256.new(plaintext)
        signature = PKCS1_v1_5.new(privatekey)
        signature = signature.sign(myhash)
        #СОБРАТЬ МАССИВ
        for item in online_users:
            plaintext = data['msg'].encode('utf-8')
            publickey = RSA.importKey(open("D:\SSI project\\TXT_For_Chat\\" + item + "publickey.txt", 'rb').read())
            cipherrsa = PKCS1_OAEP.new(publickey)
            ciphertext = cipherrsa.encrypt(plaintext)
            f = open("D:\SSI project\\TXT_For_Chat\\" + "For" + item + "massage.txt", 'wb')
            f.write(bytes(ciphertext))
            f.close()
            print(ciphertext)


        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        print(online_users)
        #chat_msgs.append((nickname, data['msg'])) #ПЕРЕДАЕТСЯ СООБЩЕНИE


    refresh_task.close()

    online_users.remove(nickname)
    toast("You are out of the chat room!")
    msg_box.append(put_markdown(f'📢 User `{nickname}` left the chat room!'))
    chat_msgs.append(('📢', f'User `{nickname}` left the chat room!'))

    put_buttons(['Re-enter'], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)