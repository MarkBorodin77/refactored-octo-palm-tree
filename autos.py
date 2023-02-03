import re
import time
import requests
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetMessagesRequest
from telethon.tl.functions.messages import GetHistoryRequest, ReadHistoryRequest
from telethon import TelegramClient, events, sync
import telethon.sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from getpass import getpass
from mysql.connector import connect, Error
import telebot
import config
from telebot import types, apihelper
# from socks import SOCKS5, SOCKS4, HTTP

TOKEN = config.bot_logi_token
bot = telebot.TeleBot(TOKEN)
API_ID = 988074
API_HASH = 'a5ec8b7b6dbeedc2514ca7e4ba200c13'


def proxis(id_akk):
    try:
        connection = connect(host=config.bd_host,user=config.bd_login,password=config.bd_pass,database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT proxi FROM akk where id =  "{id_akk}"')
        proxi = q.fetchone()[0]
        return proxi
    except Exception as e:
        return 'no'

def main():
    connection = connect(host=config.bd_host,user=config.bd_login,password=config.bd_pass,database=config.bd_base)
    q = connection.cursor()
    q.execute(f"SELECT * FROM akk where auto = 'Работает'")
    row = q.fetchall()
    for i in row: 
        try:
            print(i[0])
            proxi = proxis(i[0])   
            login_prox = proxi.split('@')[0].split(':')[0]
            pass_prox = proxi.split('@')[0].split(':')[1]
            ip_prox = proxi.split('@')[1].split(':')[0]
            port_prox = proxi.split('@')[1].split(':')[1]
            proxy = {'proxy_type':'socks5','addr': str(ip_prox),'port': int(port_prox),'username':str(login_prox),'password': str(pass_prox),'rdns': True}
            client = TelegramClient(str(i[0]), API_ID, API_HASH, device_model="Ids bot", system_version="6.12.0", app_version="10 P (28)", proxy=proxy)
            try:
                client.disconnect()
            except Exception as e:
                pass
            client.connect()
            text = i
            status_akk = client.is_user_authorized()
            if status_akk == True:
                client.parse_mode = 'html'
                dialogs = client.get_dialogs()
                for chat in dialogs:
                    id_chat = str(chat.id)
                    if id_chat[:4] != '-100':
                        if int(chat.unread_count) >= 1:
                            try:
                                client.send_message(chat.id, i[5], parse_mode='html')
                                client.send_read_acknowledge(chat.id)
                            except Exception as e:
                                pass

            else:
                try:
                    bot.send_message(i[1], f'✖️ Ошибка аккаунта | {i[0]}', reply_markup=keyboard)
                except Exception as e:
                    pass
                

            try:
                client.disconnect()
            except Exception as e:
                pass
        except Exception as e:
            try:
                bot.send_message(i[1], f'✖️ Ошибка: {e} | {i[1]}')
                client.disconnect()
            except Exception as e:
                try:
                    client.disconnect()
                except Exception as e:
                    pass
while True:
    main()
    time.sleep(300)

