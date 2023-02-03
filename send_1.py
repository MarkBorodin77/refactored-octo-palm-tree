import re
import time
import requests
import datetime
import time
from datetime import datetime, timedelta
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetMessagesRequest
from telethon.tl.functions.messages import GetHistoryRequest, ReadHistoryRequest
from telethon import TelegramClient, events, sync
import telethon.sync
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
import telebot
from telebot import types, apihelper
from telethon import errors
import re
import config
import os, random, shutil, subprocess
from getpass import getpass
from mysql.connector import connect, Error

bot = telebot.TeleBot(config.bot_logi_token)
API_ID = 988074
API_HASH = 'a5ec8b7b6dbeedc2514ca7e4ba200c13'

keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(text='↗️  Актуальная ссылка на бот', url='https://qcode.store/bot/'))


def main():
    try:
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor(buffered=True)
        q.execute(f"SELECT * FROM list_chat where status = 'Send'")
        row = q.fetchall()
        for i in row:
            try:
                q.execute(f"update list_chat set status = 'NoSend' where id_str = '{i[0]}'")
                connection.commit()
                q.execute(f"update list_chat set colvo_send = colvo_send + '1' where id_str = '{i[0]}'")
                connection.commit()
            except Exception as e:
                pass
            try:
                q.execute(f'SELECT proxi FROM akk where id =  "{i[7]}"')
                proxi = q.fetchone()[0]
                if proxi != False:
                    login_prox = proxi.split('@')[0].split(':')[0]
                    pass_prox = proxi.split('@')[0].split(':')[1]
                    ip_prox = proxi.split('@')[1].split(':')[0]
                    port_prox = proxi.split('@')[1].split(':')[1]
                    proxy = {'proxy_type': 'socks5', 'addr': str(ip_prox), 'port': int(port_prox),
                             'username': str(login_prox), 'password': str(pass_prox), 'rdns': True}
                    client = TelegramClient(str(i[7]), API_ID, API_HASH, device_model="Ids bot",
                                            system_version="6.12.0", app_version="10 P (28)", proxy=proxy)
                    client.connect()
                    client.parse_mode = 'html'
                    status_akk = client.is_user_authorized()
                    if status_akk == True:
                        d_text = i[11]
                        if d_text == None:
                            d_text = ''

                        if str(d_text) == '0':
                            d_text = ''

                        if str(d_text) == '[]':
                            d_text = ''
                        try:
                            try:
                                client.send_message(i[1], f'''{i[2]}\n{d_text}''', file=i[6], parse_mode='html')
                                tomorrow = datetime.now()
                                q.execute("INSERT INTO logi (user,chat,msg,data) VALUES ('%s','%s','%s','%s')" % (
                                i[8], i[1], i[2], tomorrow))
                                connection.commit()
                                try:
                                    bot.send_message(i[8], f'''✔️ Успешная отправка | {i[3]} | {i[7]}''')
                                except:
                                    pass
                            except:
                                client.send_message(i[1], f'''{i[2]}\n{d_text}''', parse_mode='html')
                                tomorrow = datetime.now()
                                q.execute("INSERT INTO logi (user,chat,msg,data) VALUES ('%s','%s','%s','%s')" % (
                                i[8], i[1], i[2], tomorrow))
                                connection.commit()
                                try:
                                    bot.send_message(i[8], f'''✔️ Успешная отправка | {i[3]} | {i[7]}''')
                                except:
                                    pass

                        except errors.FloodWaitError as e:
                            try:
                                bot.send_message(i[8],
                                                 f'''⏳ Flood control Have to sleep: {e.seconds} seconds !| {i[3]}''')
                            except Exception as e:
                                pass

                        except errors.SlowModeWaitError as e:
                            try:
                                bot.send_message(i[8],
                                                 f'''⏳ Flood control Have to sleep: {e.seconds} seconds !| {i[3]}''')
                            except Exception as e:
                                pass

                        except Exception as e:
                            q.execute(f"DELETE FROM list_chat where id_str = '{i[0]}'")
                            connection.commit()
                            bot.send_message(config.chat_logi_error,
                                             f'🗑 Чат: {i[3]} удален тк нет доступа к сообщениям !')
                            try:
                                bot.send_message(i[8], f'🗑 Чат: {i[3]} удален тк нет доступа к сообщениям !')
                            except:
                                pass
                    else:
                        try:
                            bot.send_message(i[8], f'✖️ Ошибка аккаунта или прокси | {i[7]}')
                        except:
                            pass
                else:
                    pass
                client.disconnect()

            except Exception as e:
                status = re.search(str('(Connection to Telegram failed)'), str(e))
                if status != None:
                    try:
                        bot.send_message(i[8], f'✖️ Ошибка аккаунта или прокси | {i[7]}')
                    except Exception as e:
                        pass
                else:
                    bot.send_message(config.chat_logi_error, f'❓ Ошибка: {e}| {i[7]}')
                try:
                    client.disconnect()
                except:
                    pass

    except Exception as e:
        bot.send_message(config.chat_logi_error, f'❓ Ошибка: {e}')


while True:
    main()
