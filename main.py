# -*- coding: utf-8 -*-
from decimal import *
import telebot
import datetime
from telebot import types, apihelper
import sqlite3
import random
import string
import time
import os
import random
import shutil
import subprocess
import json
import keyboards
import requests
from datetime import datetime, timedelta
import chat_list
from datetime import date
from dateutil.relativedelta import relativedelta
import secrets
import hashlib
import config
from getpass import getpass
from mysql.connector import connect, Error
import pytz
from qiwipyapi import Wallet

TOKEN = config.bot_osnova_token
bot = telebot.TeleBot(TOKEN)
admin = config.admin

QIWI_SEC_TOKEN = 'e16eab84d3d2f325aa07fdedca3bad5d'
wallet_number = '79361070977'  # without +

wallet_p2p = Wallet(wallet_number, p2p_sec_key=QIWI_SEC_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    if message.chat.type == 'private':
        userid = str(message.chat.id)
        username = str(message.from_user.username)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT * FROM ugc_users WHERE id = "{userid}"')
        row = q.fetchall()
        if str(row) == '[]':
            q.execute(
                "INSERT INTO ugc_users (id,data) VALUES ('%s','%s')" % (userid, 'Нет'))
            connection.commit()
            if message.text[7:] != '':
                if message.text[7:] != userid:
                    q.execute("update ugc_users set ref = " +
                              str(message.text[7:]) + " where id = " + str(userid))
                    connection.commit()
                    q.execute(
                        "update ugc_users set ref_colvo = ref_colvo + 1 where id = " + str(message.text[7:]))
                    connection.commit()
                    bot.send_message(message.text[7:], f'➕ Новый партнер: @{message.from_user.username}',
                                     reply_markup=keyboards.main)

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f'''💢 Как работает сервис ?!''',
                                                    url=f'https://telegra.ph/Informaciya-po-proektu-10-06'))
            bot.send_message(message.chat.id,
                             f'💡 Перед началом использования сервиса, пожалуйста, ознакомьтесь со статьей: https://telegra.ph/Informaciya-po-proektu-10-06',
                             parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)

        bot.send_message(message.chat.id, f'👑 Добро пожаловать в бот для автопостинга !', parse_mode='HTML',
                         reply_markup=keyboards.main)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.chat.type == 'private':
        if message.text.lower() == '/admin':
            if message.chat.id == admin:
                connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                     database=config.bd_base)
                q = connection.cursor()
                q.execute(f'SELECT COUNT(id) FROM ugc_users')
                all_user_count = q.fetchone()[0]

                q.execute(f'SELECT COUNT(id) FROM ugc_users WHERE data != "Нет"')
                all_user_podpiska = q.fetchone()[0]

                q.execute(f'SELECT COUNT(id) FROM akk')
                akkakk = q.fetchone()[0]

                q.execute(f'SELECT COUNT(id) FROM list_chat')
                chat = q.fetchone()[0]

                q.execute(f'SELECT COUNT(id) FROM logi')
                colvo_send_1 = q.fetchone()[0]

                q.execute(f'SELECT SUM(colvo_send) FROM list_chat')
                colvo_sends = q.fetchone()[0]

                q.execute(
                    f'SELECT COUNT(id) FROM list_chat WHERE status = "Send"')
                chat_no_send = q.fetchone()[0]

                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text='Пользователи', callback_data=f'admin_search_user'),
                             types.InlineKeyboardButton(text='Чаты', callback_data=f'admin_search_chat'))
                keyboard.add(types.InlineKeyboardButton(text='Рассылка', callback_data='send_sms_bot'),
                             types.InlineKeyboardButton(text='Удалить аккаунт', callback_data='del_akkss'))
                keyboard.add(types.InlineKeyboardButton(text='Обновить время', callback_data='timeupdate'),
                             types.InlineKeyboardButton(text='Перезагрузка', callback_data='restartsssss'))
                keyboard.add(types.InlineKeyboardButton(
                    text='Смена прайса', callback_data='сменапрайса'))
                bot.send_message(message.chat.id, f'''▪️Всего пользователей: {all_user_count}
▪️Подписок {all_user_podpiska}
▪️Аккаунтов: {akkakk}
▪️Чатов: {chat} 
▪️Отправлено: {colvo_sends}
▪️Успешно: {colvo_send_1}
▪️Очередь: {chat_no_send}''', parse_mode='HTML', reply_markup=keyboard)

        elif message.text.lower() == '🎛 меню':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f'''⏳ Автопостинг''', callback_data=f'akks'),
                         types.InlineKeyboardButton(text=f'''💬 Автоответчик''', callback_data=f'Автоответчик'))
            keyboard.add(types.InlineKeyboardButton(text=f'''🖥 Профиль''', callback_data=f'profale'),
                         types.InlineKeyboardButton(text=f'''📖 Информация''', callback_data=f'info'))
            bot.send_message(message.chat.id, f'''◾️ Выберите нужный пункт меню:''', parse_mode='HTML',
                             reply_markup=keyboard)
            return


def check_time_difference(t1: datetime, t2: datetime):
    t1_date = datetime(
        t1.year,
        t1.month,
        t1.day,
        t1.hour,
        t1.minute,
        t1.second)

    t2_date = datetime(
        t2.year,
        t2.month,
        t2.day,
        t2.hour,
        t2.minute,
        t2.second)

    t_elapsed = t1_date - t2_date

    return t_elapsed


def new_data(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=f'''⬅️ Назад''', callback_data=f'akks'))
    if message.text != '🎛 Меню':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f'SELECT chat FROM ugc_users where id =  "{message.chat.id}"')
        chat_chat = q.fetchone()[0]
        q = connection.cursor()
        if int(tipsend) == 4:
            q.execute(
                f"update list_chat set photo = '{message.text}' where id_str = '{chat_chat}'")
            connection.commit()
        if int(tipsend) == 1:
            q.execute(
                f"update list_chat set username = '{message.text}' where id_str = '{chat_chat}'")
            connection.commit()
        if int(tipsend) == 6:
            q.execute(
                f"update list_chat set dop_text = '{message.text}' where id_str = '{chat_chat}'")
            connection.commit()
        if int(tipsend) == 2:
            if int(message.text) >= 1:
                q.execute(
                    f"update list_chat set time = '{message.text}' where id_str = '{chat_chat}'")
                connection.commit()
                clock_in_half_hour = datetime.now() + timedelta(minutes=(int(message.text)))
                q.execute(
                    f"update list_chat set time_step = '{clock_in_half_hour.hour}:{clock_in_half_hour.minute}' where id_str = '{chat_chat}'")
                connection.commit()
        bot.send_message(message.chat.id, '✔️ Готово',
                         parse_mode='HTML', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Отменили',
                         parse_mode='HTML', reply_markup=keyboard)


def new_data_m(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=f'''⬅️ Назад''', callback_data=f'akks'))
    if message.text != '🎛 Меню':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT akk FROM ugc_users where id =  "{message.chat.id}"')
        chat_chat = q.fetchone()[0]
        if int(tipsend11) == 4:
            q.execute(
                f"update list_chat set photo = '{message.text}' where akk = '{chat_chat}'")
            connection.commit()
            bot.send_message(message.chat.id, '✔️ Готово',
                             parse_mode='HTML', reply_markup=keyboard)
        if int(tipsend11) == 1:
            q.execute(
                f"update list_chat set username = '{message.text}' where akk = '{chat_chat}'")
            connection.commit()
            bot.send_message(message.chat.id, '✔️ Готово',
                             parse_mode='HTML', reply_markup=keyboard)

        if int(tipsend11) == 5:
            try:
                id_old_akk = message.text.split('\n')[0]
                id_new_akk = message.text.split('\n')[1]
                q.execute(
                    f"SELECT * FROM list_chat where akk = '{id_old_akk}'")
                row = q.fetchall()
                for i in row:
                    q.execute(
                        "INSERT INTO list_chat (id,username,name,time,time_step,photo,akk,id_user,status,colvo_send,dop_text) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                            i[1], i[2], i[3], i[4], i[5], i[6], id_new_akk, i[8], i[9], i[10], i[11]))
                    connection.commit()
                    print(i[0])
                bot.send_message(message.chat.id, '✔️ Готово',
                                 parse_mode='HTML', reply_markup=keyboard)
            except Exception as e:
                bot.send_message(
                    message.chat.id, f'✖️ Ошибка: {e}', parse_mode='HTML', reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Отменили',
                         parse_mode='HTML', reply_markup=keyboard)


def smena_prace(message):
    if message.text != 'Отмена':
        ned = message.text.split('\n')[0]
        mes = message.text.split('\n')[1]
        s2mes = message.text.split('\n')[2]
        life = message.text.split('\n')[3]
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f"update config set ned = '{ned}' where id = '1'")
        connection.commit()
        q.execute(f"update config set mes = '{mes}' where id = '1'")
        connection.commit()
        q.execute(f"update config set 2mes = '{s2mes}' where id = '1'")
        connection.commit()
        q.execute(f"update config set life = '{life}' where id = '1'")
        connection.commit()
        bot.send_message(
            message.chat.id, 'Успешно!  | /admin', parse_mode='HTML')


def send_photoorno(message):
    if message.text != 'Отмена':
        global text_send_all
        text_send_all = message.text
        msg = bot.send_message(message.chat.id, 'Отправьте ссылку на медиа', parse_mode='HTML',
                               disable_web_page_preview=True)
        bot.register_next_step_handler(msg, admin_send_message_all_text_rus)


def admin_send_message_all_text_rus(message):
    if message.text != 'Отмена':
        global media
        media = message.text
        if int(tipsendSSSSS) == 1:
            msg = bot.send_photo(message.chat.id, str(media),
                                 "Отправить всем пользователям уведомление:\n" +
                                 text_send_all + '\n\nЕсли вы согласны, напишите Да',
                                 parse_mode='HTML')
            bot.register_next_step_handler(
                msg, admin_send_message_all_text_da_rus)

        if int(tipsendSSSSS) == 2:
            msg = bot.send_animation(chat_id=message.chat.id, animation=media,
                                     caption="Отправить всем пользователям уведомление:\n" +
                                     text_send_all + '\n\nЕсли вы согласны, напишите Да',
                                     parse_mode='HTML')
            bot.register_next_step_handler(
                msg, admin_send_message_all_text_da_rus)

        if int(tipsendSSSSS) == 3:
            media = f'<a href="{media}">.</a>'
            msg = bot.send_message(message.chat.id, f'''Отправить всем пользователям уведомление:
{text_send_all}
{media}
Если вы согласны, напишите Да''', parse_mode='HTML')
            bot.register_next_step_handler(
                msg, admin_send_message_all_text_da_rus)


def admin_send_message_all_text_da_rus(message):
    otvet = message.text
    colvo_send_message_users = 0
    colvo_dont_send_message_users = 0
    if message.text != 'Отмена':
        if message.text.lower() == 'Да'.lower():
            connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                 database=config.bd_base)
            with connection:
                q = connection.cursor()
                bot.send_message(message.chat.id, 'Начинаем отправлять!')
                if int(tipsendSSSSS) == 1:  # картинка
                    q.execute("SELECT * FROM ugc_users")
                    row = q.fetchall()
                    for i in row:
                        jobid = i[0]

                        time.sleep(0.1)
                        reply = json.dumps(
                            {'inline_keyboard': [[{'text': '✖️ Закрыть', 'callback_data': f'Главное'}]]})
                        response = requests.post(
                            url='https://api.telegram.org/bot{0}/{1}'.format(
                                TOKEN, "sendPhoto"),
                            data={'chat_id': jobid, 'photo': str(media), 'caption': str(text_send_all),
                                  'reply_markup': str(reply), 'parse_mode': 'HTML'}
                        ).json()
                        if response['ok'] == False:
                            colvo_dont_send_message_users = colvo_dont_send_message_users + 1
                            q.execute(
                                f"DELETE FROM ugc_users where id = '{jobid}'")
                            connection.commit()
                        else:
                            colvo_send_message_users = colvo_send_message_users + 1
                    bot.send_message(message.chat.id, 'Отправлено сообщений: ' + str(
                        colvo_send_message_users) + '\nНе отправлено: ' + str(colvo_dont_send_message_users))

                elif int(tipsendSSSSS) == 2:  # гиф
                    q.execute("SELECT * FROM ugc_users")
                    row = q.fetchall()
                    for i in row:
                        jobid = i[0]

                        time.sleep(0.1)
                        reply = json.dumps(
                            {'inline_keyboard': [[{'text': '✖️ Закрыть', 'callback_data': f'Главное'}]]})
                        response = requests.post(
                            url='https://api.telegram.org/bot{0}/{1}'.format(
                                TOKEN, "sendAnimation"),
                            data={'chat_id': jobid, 'animation': str(media), 'caption': str(text_send_all),
                                  'reply_markup': str(reply), 'parse_mode': 'HTML'}
                        ).json()
                        if response['ok'] == False:
                            colvo_dont_send_message_users = colvo_dont_send_message_users + 1
                        else:
                            colvo_send_message_users = colvo_send_message_users + 1
                    bot.send_message(message.chat.id, 'Отправлено сообщений: ' + str(
                        colvo_send_message_users) + '\nНе отправлено: ' + str(colvo_dont_send_message_users))

                elif int(tipsendSSSSS) == 3:  # видео
                    q.execute("SELECT * FROM ugc_users")
                    row = q.fetchall()
                    for i in row:
                        jobid = i[0]
                        time.sleep(0.2)
                        response = requests.post(
                            url='https://api.telegram.org/bot{0}/{1}'.format(
                                TOKEN, "sendMessage"),
                            data={'chat_id': jobid, 'text': str(
                                text_send_all) + str(media), 'parse_mode': 'HTML'}
                        ).json()
                        if response['ok'] == False:
                            colvo_dont_send_message_users = colvo_dont_send_message_users + 1
                            q.execute(
                                f"DELETE FROM ugc_users where id = '{jobid}'")
                            connection.commit()

                        else:
                            colvo_send_message_users = colvo_send_message_users + 1
                    bot.send_message(message.chat.id, 'Отправлено сообщений: ' + str(
                        colvo_send_message_users) + '\nНе отправлено: ' + str(colvo_dont_send_message_users))


def add_money2(message):
    if message.text != 'Отмена':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"update ugc_users set balance = '{message.text}' where id = '{id_user_edit_bal1}'")
        connection.commit()
        q.execute("select ref from ugc_users where id = " +
                  str(id_user_edit_bal1))
        ref_user1 = q.fetchone()[0]
        if ref_user1 != None:
            add_deposit = int(message.text) / 100 * 25
            q.execute("update ugc_users set balance = balance + " +
                      str(add_deposit) + " where id =" + str(ref_user1))
            connection.commit()
            try:
                bot.send_message(ref_user1, f'Реферал пополнил баланс и вам зачислинно {add_deposit} RUB',
                                 parse_mode='HTML')
            except Exception as e:
                pass
        bot.send_message(
            message.chat.id, 'Успешно!  | /admin', parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id, 'Вернулись в админку | /admin', parse_mode='HTML')


def searchuser(message):
    if message.text.lower() != 'отмена':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f"SELECT * FROM ugc_users where id = '{message.text}'")
        row = q.fetchone()
        bot.send_message(message.chat.id, '<b>🔍 Ищем...</b>',
                         parse_mode='HTML', reply_markup=keyboards.main)
        if row != None:
            q.execute(f"SELECT COUNT(id) FROM akk where user = '{row[0]}'")
            saasssss = q.fetchone()[0]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text='➕ Добавить баланс', callback_data=f'добавитьбаланс_{row[0]}'))
            msg = bot.send_message(message.chat.id, f'''<b>Подробнее:</b>
<b>Ид:</b> <code>{row[0]}</code>
<b>Баланс:</b> <code>{row[1]}</code>
<b>Аккаунтов:</b> <code>{saasssss}</code>
<b>Подписка:</b> <code>{row[5]}</code>
''', parse_mode='HTML', reply_markup=keyboard)
        else:
            bot.send_message(
                message.chat.id, '<b>Нет такого пользователя</b> | /admin', parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id, '<b>Отменили</b> | /admin', parse_mode='HTML')


def delakks(message):
    if message.text.lower() != 'отмена':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f"DELETE FROM list_chat where akk = '{message.text}'")
        connection.commit()
        q.execute(f"DELETE FROM akk where id = '{message.text}'")
        connection.commit()
        bot.send_message(
            message.chat.id, f'''✔️ Аккаунт успешно удален | /admin''', parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id, '<b>Отменили</b> | /admin', parse_mode='HTML')


def searchchat(message):
    if message.text.lower() != 'отмена':
        bot.send_message(message.chat.id, '<b>🔍 Ищем...</b>',
                         parse_mode='HTML', reply_markup=keyboards.main)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f"SELECT data FROM ugc_users where id = '{message.chat.id}'")
        datas = q.fetchone()[0]
        if str(datas) != str('Нет'):
            q.execute(
                f"update ugc_users set akk = '{message.text}' where id = '{message.chat.id}'")
            connection.commit()
            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{message.chat.id}"')
            akk_akk = q.fetchone()[0]
            q.execute(f'SELECT proxi FROM akk where id =  "{akk_akk}"')
            proxi = q.fetchone()[0]
            keyboard = types.InlineKeyboardMarkup()
            q.execute(f"SELECT * FROM list_chat  where akk = '{akk_akk}'")
            rows = q.fetchall()
            btns = []
            for i in range(len(rows)):
                btns.append(types.InlineKeyboardButton(
                    text=rows[i][3], callback_data=f'servis_{rows[i][0]}'))
            while btns != []:
                try:
                    keyboard.add(
                        btns[0],
                        btns[1]
                    )
                    del btns[1], btns[0]
                except:
                    keyboard.add(btns[0])
                    del btns[0]

            keyboard.add(
                types.InlineKeyboardButton(text=f'''🔄  Загрузить чаты с аккаунта''', callback_data=f'loading_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''🌏 Смена прокси''', callback_data=f'сменапрокси'),
                         types.InlineKeyboardButton(text=f'''🗑 Удалить аккаунт''', callback_data=f'del_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''⬅️ Назад''', callback_data=f'akks'),
                         types.InlineKeyboardButton(text=f'''📚 Multi settings''', callback_data=f'Multi'))
            bot.send_message(
                message.chat.id, f'''🌐 Прокси: {proxi}''', parse_mode='HTML', reply_markup=keyboard)
        else:
            bot.send_message(
                message.chat.id, '<b>Ошибка</b> | /admin', parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id, '<b>Отменили</b> | /admin', parse_mode='HTML')


def add_proxi(message):
    if message.text != '🎛 Меню':
        try:
            proxi = message.text
            login_prox = proxi.split('@')[0].split(':')[0]
            pass_prox = proxi.split('@')[0].split(':')[1]
            ip_prox = proxi.split('@')[1].split(':')[0]
            port_prox = proxi.split('@')[1].split(':')[1]
            connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                 database=config.bd_base)
            q = connection.cursor()
            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{message.chat.id}"')
            akkkkkkk = q.fetchone()[0]
            q.execute(
                f"update akk set proxi = '{proxi}' where id = '{akkkkkkk}'")
            connection.commit()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(message.chat.id, F'''✔️ Успешно сменили прокси''', parse_mode='HTML',
                             reply_markup=keyboard)
        except Exception as e:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(message.chat.id, f'✖️ Ошибка формата',
                             parse_mode='HTML', reply_markup=keyboard)
    else:
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'akks'))
        bot.send_message(
            message.chat.id, '✔️ Вернулись на главную', reply_markup=keyboard)


def add_autotext(message):
    if message.text != '🎛 Меню':
        try:
            connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                 database=config.bd_base)
            q = connection.cursor()
            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{message.chat.id}"')
            akkkkkkk = q.fetchone()[0]
            q.execute(
                f"update akk set text = '{message.text}' where id = '{akkkkkkk}'")
            connection.commit()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'Автоответчик'))
            bot.send_message(message.chat.id, F'''✔️ Успешно сменили''',
                             parse_mode='HTML', reply_markup=keyboard)
        except Exception as e:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'Автоответчик'))
            bot.send_message(message.chat.id, f'✖️ Ошибка формата',
                             parse_mode='HTML', reply_markup=keyboard)
    else:
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Автоответчик'))
        bot.send_message(
            message.chat.id, '✔️ Вернулись на главную', reply_markup=keyboard)


def proxis(id_akk):
    connection = connect(host=config.bd_host, user=config.bd_login,
                         password=config.bd_pass, database=config.bd_base)
    q = connection.cursor()
    q.execute(f'SELECT proxi FROM akk where id =  "{id_akk}"')
    proxi = q.fetchone()[0]
    return proxi


def generator_pw():
    pwd = string.digits
    return "".join(random.choice(pwd) for x in range(random.randint(16, 16)))


def btc_oplata_1(message):
    if message.text != 'Отмена':
        try:
            if int(message.text) >= int(1):
                connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                     database=config.bd_base)
                q = connection.cursor()
                id_pay = generator_pw()
                invoice = wallet_p2p.create_invoice(value=int(message.text))
                url = invoice['payUrl']
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(
                    text=f'''↗️ Перейти к оплате ''', url=url))
                keyboard.add(types.InlineKeyboardButton(text=f'''✔️ Проверить оплату''',
                                                        callback_data=f"proverkaqiwi{invoice['billId']}"))
                keyboard.add(types.InlineKeyboardButton(
                    text=f'''⬅️ Назад''', callback_data=f'profale'))
                bot.send_message(message.chat.id, '''▪️  Для пополнения баланса перейдите по ссылке и оплатите счет удобным способом !

    💡 После оплаты нажмите кнопку для проверки.''', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, f'✖️ Минимальная сумма оплаты 2 RUB', parse_mode='HTML',
                                 reply_markup=keyboards.main)
        except Exception as e:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'profale'))
            bot.send_message(message.chat.id, f'✖️ Минимальная сумма оплаты 2 RUB', parse_mode='HTML',
                             reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Вернулись на главную',
                         reply_markup=keyboards.main)


@bot.callback_query_handler(func=lambda call: True)
def podcategors(call):
    if call.data == 'akks':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f"SELECT * FROM akk where user = '{call.message.chat.id}'")
        row = q.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for i in row:
            keyboard.add(types.InlineKeyboardButton(
                text=i[2], callback_data=f'список{i[0]}'))
        keyboard.add(types.InlineKeyboardButton(
            text='➕ Добавить аккаунт', callback_data=f'добавитьаккаунт'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.from_user.id, f'''◾️ Выберите нужный аккаунт или добавьте новый:''', parse_mode='HTML',
                         reply_markup=keyboard)

    if call.data == 'Автоответчик':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        keyboard = types.InlineKeyboardMarkup()
        q.execute(f"SELECT * FROM akk where user = '{call.message.chat.id}'")
        row = q.fetchall()
        keyboard = types.InlineKeyboardMarkup()
        for i in row:
            keyboard.add(types.InlineKeyboardButton(
                text=i[2], callback_data=f'автоответ{i[0]}'))
        keyboard.add(types.InlineKeyboardButton(
            text='➕ Добавить аккаунт', callback_data=f'добавитьаккаунт'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.from_user.id, f'''◾️ Выберите нужный аккаунт или добавьте новый:''', parse_mode='HTML',
                         reply_markup=keyboard)

    if call.data[:12] == 'proverkaqiwi':
        billllid = call.data[12:]
        status = wallet_p2p.invoice_status(bill_id=billllid)
        if str(status['status']['value']) == str('PAID'):
            connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                                 database=config.bd_base)
            q = connection.cursor()
            q.execute(
                f"update ugc_users set balance = balance + '{status['amount']['value']}' where id = '{call.from_user.id}'")
            connection.commit()
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            bot.send_message(call.from_user.id, f"✔️ Баланс пополнен на {status['amount']['value']} RUB",
                             parse_mode='HTML')
            bot.send_message(config.admin,
                             f"Баланс <a href='tg://user?id={call.message.chat.id}'>{call.message.chat.first_name}</a> пополнен на {status['amount']['value']} RUB",
                             parse_mode="HTML")

        else:
            bot.answer_callback_query(
                callback_query_id=call.id, show_alert=True, text="Оплата не найдена")

    if call.data[:9] == 'автоответ':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"SELECT data FROM ugc_users where id = '{call.message.chat.id}'")
        datas = q.fetchone()[0]
        if str(datas) != str('Нет'):

            q.execute(
                f"update ugc_users set akk = '{call.data[9:]}' where id = '{call.message.chat.id}'")
            connection.commit()

            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
            akk_akk = q.fetchone()[0]

            q.execute(f'SELECT proxi FROM akk where id =  "{akk_akk}"')
            proxi = q.fetchone()[0]

            q.execute(f'SELECT auto FROM akk where id =  "{akk_akk}"')
            status_auto = q.fetchone()[0]

            q.execute(f'SELECT text FROM akk where id =  "{akk_akk}"')
            text_auto = q.fetchone()[0]
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f'''💬 Смена текста''', callback_data=f'текста'),
                         types.InlineKeyboardButton(text=f'''💡Вкл/Выкл автоответчик''',
                                                    callback_data=f'вклавтооответчик'))
            keyboard.add(types.InlineKeyboardButton(text=f'''🌏 Смена прокси''', callback_data=f'сменапрокси'),
                         types.InlineKeyboardButton(text=f'''🗑 Удалить аккаунт''', callback_data=f'del_akk'))
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.message.chat.id, f'''▪️ Прокси: {proxi}
    ▪️ Текст автооответчика: {text_auto}
    ▪️ Статус: {status_auto}''', parse_mode='HTML', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'), )
            bot.send_message(call.message.chat.id, f'''✖️ Подписка отсутствует''', parse_mode='HTML',
                             reply_markup=keyboard)

    if call.data == 'текста':
        msg = bot.send_message(call.message.chat.id, 'ℹ️ Введите текст автоответчика:', parse_mode='HTML',
                               reply_markup=keyboards.main)
        bot.register_next_step_handler(msg, add_autotext)

    if call.data == 'ref':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()

        q.execute(
            f"SELECT ref_colvo FROM ugc_users where id = '{call.message.chat.id}'")
        colvo_ref = q.fetchone()[0]

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f'''🥇Топ партнеров''', callback_data=f'top_ref'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'profale'))
        bot.send_message(call.message.chat.id, f'''🗣 Партнерская программа

💸 Чтобы пассивно капали деньги на баланс, многого не нужно. Зови друзей и получай с них монету😉

📈 У вас: {colvo_ref} реферал(ов).

🌐 Ссылка для приглашения: https://t.me/{config.bot_osnova_name}?start={call.message.chat.id}

❗️Вы получаете 25% с пополнений рефералов.

⚠️ Запрещена регистрация мультиаккаунтов с целью получения партнерских выплат, т.е. нельзя быть рефералом самому себе.''',
                         reply_markup=keyboard, disable_web_page_preview=True)

    if call.data == 'вклавтооответчик':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()

        q.execute(
            f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
        akk_akk = q.fetchone()[0]

        q.execute(f'SELECT auto FROM akk where id =  "{akk_akk}"')
        status_auto = q.fetchone()[0]
        if str(status_auto) == str('Выключен'):
            q.execute(
                f"update akk set auto = 'Работает' where id = '{akk_akk}'")
            connection.commit()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'Автоответчик'))
            bot.send_message(call.message.chat.id, F'''✔️ Успешно включили''',
                             parse_mode='HTML', reply_markup=keyboard)
        else:
            q.execute(
                f"update akk set auto = 'Выключен' where id = '{akk_akk}'")
            connection.commit()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'Автоответчик'))
            bot.send_message(call.message.chat.id, F'''✔️ Успешно выключили''', parse_mode='HTML',
                             reply_markup=keyboard)

    if call.data == 'timeupdate':
        bot.send_message(call.from_user.id, 'Load', parse_mode='HTML')
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        clock_in_half_hour = datetime.now()
        q.execute(f"SELECT * FROM list_chat where time >= '1'")
        row = q.fetchall()
        for i in row:
            ttt = datetime.now() + timedelta(minutes=(int(i[4])))
            q.execute(
                f"update list_chat set time_step = '{ttt.hour}:{ttt.minute}' where id_str = '{i[0]}'")
            connection.commit()

        bot.send_message(call.from_user.id,
                         f'''✔️ Time update /admin''', parse_mode='HTML')

    if call.data == 'restartsssss':
        bot.send_message(call.message.chat.id,
                         '<b>Начинаем...</b>', parse_mode='HTML')
        cmd = 'systemctl restart avp'
        cmd1 = 'systemctl restart avp_autos'
        cmd2 = 'systemctl restart avp_bot_auch'
        cmd3 = 'systemctl restart avp_ids_spam'
        cmd4 = 'systemctl restart avp_send_1'
        subprocess.Popen(cmd3, shell=True)
        subprocess.Popen(cmd1, shell=True)
        subprocess.Popen(cmd2, shell=True)
        subprocess.Popen(cmd4, shell=True)
        subprocess.Popen(cmd, shell=True)

    if call.data[:6] == 'список':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"SELECT data FROM ugc_users where id = '{call.message.chat.id}'")
        datas = q.fetchone()[0]
        if str(datas) != str('Нет'):

            q.execute(
                f"update ugc_users set akk = '{call.data[6:]}' where id = '{call.message.chat.id}'")
            connection.commit()

            print(call.data[6:])

            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
            akk_akk = q.fetchone()[0]
            print(akk_akk)

            q.execute(f'SELECT proxi FROM akk where id =  "{akk_akk}"')
            proxi = q.fetchone()[0]

            keyboard = types.InlineKeyboardMarkup()

            q.execute(f"SELECT * FROM list_chat  where akk = '{akk_akk}'")
            rows = q.fetchall()

            btns = []
            for i in range(len(rows)):
                btns.append(types.InlineKeyboardButton(
                    text=rows[i][3], callback_data=f'servis_{rows[i][0]}'))
            while btns != []:
                try:
                    keyboard.add(
                        btns[0],
                        btns[1]
                    )
                    del btns[1], btns[0]
                except:
                    keyboard.add(btns[0])
                    del btns[0]

            keyboard.add(
                types.InlineKeyboardButton(text=f'''🔄  Загрузить чаты с аккаунта''', callback_data=f'loading_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''🌏 Смена прокси''', callback_data=f'сменапрокси'),
                         types.InlineKeyboardButton(text=f'''🗑 Удалить аккаунт''', callback_data=f'del_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''⬅️ Назад''', callback_data=f'akks'),
                         types.InlineKeyboardButton(text=f'''📚 Multi settings''', callback_data=f'Multi'))
            bot.send_message(
                call.message.chat.id, f'''🌐 Прокси: {proxi}''', parse_mode='HTML', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'), )
            bot.send_message(call.message.chat.id, f'''✖️ Подписка отсутствует''', parse_mode='HTML',
                             reply_markup=keyboard)

    if call.data == 'loading_akk':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        bot.send_message(
            call.message.chat.id, f'🔄 Загружаем, пожалуйста ожидайте.', reply_markup=keyboards.main)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
        akk_akk = q.fetchone()[0]
        www = chat_list.mainssssss(akk_akk, call.message.chat.id)
        if str(www) == str('ok'):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.message.chat.id, f'''✔️ Чаты успешно добавлены.

⚠️ Для получения логов у вас должен быть запущен бот: @{config.bot_logi_name}''', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.message.chat.id,
                             f'✖️ Ошибка аккаунта.', reply_markup=keyboard)

    if call.data == 'сменапрокси':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=f'''📜 Инструкция''', url='https://telegra.ph/Dobavlyaem-proksi-06-28'),
            types.InlineKeyboardButton(text=f'''➕ Купить прокси''', url='https://www.proxy.house/?r=65634'))
        msg = bot.send_message(call.message.chat.id, 'ℹ️ Введите прокси в формате: login:password@ip:port (SOCKS)',
                               parse_mode='HTML', reply_markup=keyboard)
        bot.register_next_step_handler(msg, add_proxi)

    if call.data == 'del_akk':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
        akk_akkass = q.fetchone()[0]
        q.execute(f"DELETE FROM list_chat where akk = '{akk_akkass}'")
        connection.commit()
        q.execute(f"DELETE FROM akk where id = '{akk_akkass}'")
        connection.commit()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'akks'))
        bot.send_message(call.from_user.id, f'''✔️ Аккаунт успешно удален''',
                         parse_mode='HTML', reply_markup=keyboard)

    if call.data == 'добавитьаккаунт':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"SELECT data FROM ugc_users where id = '{call.message.chat.id}'")
        datas = q.fetchone()[0]
        if str(datas) != str('Нет'):
            code = call.message.chat.id
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f'''🌐 Перейти''',
                                                    url=f'https://t.me/{config.bot_auch_name}?start={code}'))
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.message.chat.id,
                             f'''ℹ️ Перейдите в бот  <a href="https://t.me/{config.bot_auch_name}?start={code}">ссылке</a> и пройдите авторизацию следуйте дальнейшим инструкциям.''',
                             parse_mode='HTML', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.from_user.id, f'''✖️ У вас нет подписки''',
                             parse_mode='HTML', reply_markup=keyboard)

    if call.data[:7] == 'servis_':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        q.execute(
            f"update ugc_users set chat = '{call.data[7:]}' where id = '{call.message.chat.id}'")
        connection.commit()
        q.execute(
            f'SELECT chat FROM ugc_users where id =  "{call.message.chat.id}"')
        chat_chat = q.fetchone()[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Сменить текст', callback_data=f'настройка{1}'),
                     types.InlineKeyboardButton(text='Сменить доп текст', callback_data=f'настройка{6}'))
        keyboard.add(types.InlineKeyboardButton(text='Сменить фото', callback_data=f'настройка{4}'),
                     types.InlineKeyboardButton(text='Сменить задержку', callback_data=f'настройка{2}'))
        q.execute(f"SELECT * FROM list_chat where id_str = '{chat_chat}'")
        row = q.fetchone()
        try:
            keyboard.add(types.InlineKeyboardButton(
                text='Отправить сейчас', callback_data=f'Отправить{chat_chat}'))
            keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'akks'),
                         types.InlineKeyboardButton(text='Удалить', callback_data=f'настройка{3}'))
            bot.send_message(call.from_user.id, f'''▪️ Id: <code>{row[1]}</code>
▪️ Текст: {row[2]}
▪️ Доп текст: {row[11]}
▪️ Картинка: <code>{row[6]}</code> (ссылка)
▪️ Задержка: <code>{row[4]}</code> минут
▪️ Отправка: <code>{row[5]}</code>''', parse_mode='HTML', reply_markup=keyboard)
        except Exception as e:
            bot.send_message(call.from_user.id, f'''▪️ Id: <code>{row[1]}</code>
▪️ Текст: Ошибка форматирования поста
▪️ Доп текст: Ошибка форматирования поста
▪️ Картинка: <code>{row[6]}</code> (ссылка)
▪️ Задержка: <code>{row[4]}</code> минут
▪️ Отправка: <code>{row[5]}</code>''', parse_mode='HTML', reply_markup=keyboard)
        clock_in_half_hour = datetime.now()
        bot.send_message(call.from_user.id, f'''
▪️ Текущие время сервера: <code>{clock_in_half_hour}</code>''', parse_mode='HTML', reply_markup=keyboards.main)

    if call.data[:9] == 'Отправить':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"update list_chat set status = 'Send' where id_str = '{call.data[9:]}'")
        connection.commit()
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                  text="Отправка поставлена в очередь и будет произведена в течений минуты !")

    if call.data == 'send_sms_bot':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text='С картинокй', callback_data=f'Рассылка{1}'))
        keyboard.add(types.InlineKeyboardButton(
            text='С гиф', callback_data=f'Рассылка{2}'))
        keyboard.add(types.InlineKeyboardButton(
            text='С видео', callback_data=f'Рассылка{3}'))
        bot.send_message(call.from_user.id, f'''как будем рассылкать ?''',
                         parse_mode='HTML', reply_markup=keyboard)

    if call.data[:8] == 'Рассылка':
        global tipsendSSSSS
        tipsendSSSSS = call.data[8:]
        msg = bot.send_message(
            call.message.chat.id, "<b>Введи текст для рассылки</b>", parse_mode='HTML')
        bot.register_next_step_handler(msg, send_photoorno)

    if call.data == 'Multi':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text='Сменить текст', callback_data=f'мульти{1}'))
        keyboard.add(types.InlineKeyboardButton(
            text='Сменить фото', callback_data=f'мульти{4}'))
        keyboard.add(types.InlineKeyboardButton(
            text='Сменить задержку', callback_data=f'мульти{3}'))
        keyboard.add(types.InlineKeyboardButton(
            text='Скопировать чаты', callback_data=f'мульти{5}'))
        keyboard.add(types.InlineKeyboardButton(
            text='Назад', callback_data=f'akks'))
        bot.send_message(call.from_user.id, f'''▪️Смена информации по всем чатам аккаунта:''', parse_mode='HTML',
                         reply_markup=keyboard)

    if call.data[:6] == 'мульти':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        global tipsend11
        tipsend11 = call.data[6:]
        if int(tipsend11) == 1:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введи новое значение:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data_m)

        if int(tipsend11) == 4:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введи новое значение:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data_m)

        if int(tipsend11) == 3:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введи новое значение:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data_m)

        if int(tipsend11) == 5:
            msg = bot.send_message(call.message.chat.id, "<b>Введи старый номер аккаунта и новый с новой строки:</b>",
                                   parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data_m)

    elif call.data[:9] == 'настройка':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        global tipsend
        tipsend = call.data[9:]
        print(tipsend)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        if int(tipsend) == 1:
            msg = bot.send_message(call.message.chat.id,
                                   "Введи новое значение: (Можно использовать формат разметки 'html') | Не указывайте в тексте знаки ' ",
                                   parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data)
        if int(tipsend) == 2:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введи новое значение:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data)
        if int(tipsend) == 3:
            q.execute(
                f'SELECT chat FROM ugc_users where id =  "{call.message.chat.id}"')
            chat_chat = q.fetchone()[0]
            q.execute(f"DELETE FROM list_chat where id_str = '{chat_chat}'")
            connection.commit()
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'akks'))
            bot.send_message(call.from_user.id, '''✔️ Готово''',
                             parse_mode='HTML', reply_markup=keyboard)
        if int(tipsend) == 4:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введите ссылку на фото:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data)
        if int(tipsend) == 5:
            keyboard = types.InlineKeyboardMarkup()
            q.execute(
                f'SELECT akk FROM ugc_users where id =  "{call.message.chat.id}"')
            akk_akk = q.fetchone()[0]

            keyboard = types.InlineKeyboardMarkup()
            q.execute(f"SELECT * FROM list_chat  where akk = '{akk_akk}'")
            rows = q.fetchall()
            btns = []
            for i in range(len(rows)):
                btns.append(types.InlineKeyboardButton(
                    text=rows[i][3], callback_data=f'servis_{rows[i][0]}'))

            while btns != []:
                try:
                    keyboard.add(
                        btns[0],
                        btns[1]
                    )

                    del btns[1], btns[0]

                except:
                    keyboard.add(btns[0])
                    del btns[0]
            clock_in_half_hour = datetime.now()
            keyboard.add(
                types.InlineKeyboardButton(text=f'''🔄  Загрузить чаты с аккаунта''', callback_data=f'loading_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''🌏 Смена прокси''', callback_data=f'сменапрокси'),
                         types.InlineKeyboardButton(text=f'''🗑 Удалить аккаунт''', callback_data=f'del_akk'))
            keyboard.add(types.InlineKeyboardButton(text=f'''⬅️ Назад''', callback_data=f'akks'),
                         types.InlineKeyboardButton(text=f'''📚 Multi settings''', callback_data=f'Multi'))
        if int(tipsend) == 6:
            msg = bot.send_message(
                call.message.chat.id, "<b>Введи новое значение:</b>", parse_mode='HTML')
            bot.register_next_step_handler(msg, new_data)

    elif call.data == 'Главное':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=f'''⏳ Автопостинг''', callback_data=f'akks'),
                     types.InlineKeyboardButton(text=f'''💬 Автоответчик''', callback_data=f'Автоответчик'))
        keyboard.add(types.InlineKeyboardButton(text=f'''🖥 Профиль''', callback_data=f'profale'),
                     types.InlineKeyboardButton(text=f'''📖 Информация''', callback_data=f'info'))
        bot.send_message(call.message.chat.id, f'''◾️ Выберите нужный пункт меню:''', parse_mode='HTML',
                         reply_markup=keyboard)

    elif call.data == 'profale':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()

        q.execute(
            f"SELECT balance FROM ugc_users where id = '{call.message.chat.id}'")
        balans = q.fetchone()[0]

        q.execute(
            f"SELECT data FROM ugc_users where id = '{call.message.chat.id}'")
        data = q.fetchone()[0]

        q.execute(
            f"SELECT COUNT(id) FROM akk where user = '{call.message.chat.id}'")
        akss_id = q.fetchone()[0]

        q.execute(
            f'SELECT SUM(colvo_send) FROM list_chat where id_user = "{call.message.chat.id}"')
        colvo_sends = q.fetchone()[0]

        q.execute(
            f'SELECT COUNT(id) FROM list_chat where id_user = "{call.message.chat.id}"')
        chats = q.fetchone()[0]
        if chats == None:
            chats = 0
        if akss_id == None:
            akss_id = 0
        if colvo_sends == None:
            colvo_sends = 0
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=f'''💰 Пополнить баланс''', callback_data='Пополнить'),
                     types.InlineKeyboardButton(text=f'''🔓 Оформить подписку''', callback_data='Оформить'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''🗣 Партнерская программа''', callback_data='ref'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.message.chat.id, f'''
▪️ id: <code>{call.message.chat.id}</code>
▪️ Баланс: <code>{balans}</code> RUB
▪️ Аккаунтов: <code>{akss_id}</code>
▪️ Чатов: <code>{chats}</code>
▪️ Отправленно: <code>{colvo_sends}</code>
▪️ Подписка до: <code>{data}</code>
''', parse_mode='HTML', reply_markup=keyboard)

    elif call.data == 'Пополнить':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text=f'''▪️ QIWI / CARD / YA  / PM / BTC / LTC''', callback_data='add_depozit'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'profale'))
        bot.send_message(call.message.chat.id, f'''▪️ Выберите способ для депозита:''', parse_mode='HTML',
                         reply_markup=keyboard)

    elif call.data == 'add_depozit':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        msg = bot.send_message(call.message.chat.id, '''ℹ️ Укажите сумму пополнения:''', reply_markup=keyboards.main,
                               parse_mode='HTML')
        bot.register_next_step_handler(msg, btc_oplata_1)

    elif call.data == 'Оформить':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT * FROM config where id =  "1"')
        prace = q.fetchone()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f'''◾️ Неделя {prace[1]}р''', callback_data=f'подписка1'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''◾️ 1 месяц / {prace[2]}р''', callback_data=f'подписка2'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''◾️ 3 месяц / {prace[3]}р''', callback_data=f'подписка3'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''◾️ Безлимит / {prace[4]}р''', callback_data=f'подписка4'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.message.chat.id, '''◾️ Выберите подписку:''',
                         parse_mode='HTML', reply_markup=keyboard)

    elif call.data[:8] == 'подписка':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        temp_id = call.data[8:]
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT * FROM config where id =  "1"')
        prace = q.fetchone()
        q.execute(
            f"SELECT balance FROM ugc_users where id = '{call.from_user.id}'")
        bal_us = q.fetchone()[0]
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        if str(temp_id) == '1':
            if int(bal_us) >= int(prace[1]):
                q.execute("update ugc_users set balance = balance - " + str(prace[1]) + " where id = " + str(
                    call.from_user.id))
                connection.commit()
                tomorrow = datetime.now() + timedelta(days=7)
                tomorrow_formatted = tomorrow.strftime('%d/%m/%Y')
                print(tomorrow_formatted)
                q.execute(
                    f"update ugc_users set data = '{tomorrow_formatted}' where id = '{call.from_user.id}'")
                connection.commit()
                bot.send_message(call.message.chat.id, '''✔️ Подписка оформлена''', parse_mode='HTML',
                                 reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, '''✖️ Пополните баланс''', parse_mode='HTML',
                                 reply_markup=keyboard)

        if str(temp_id) == '2':
            if int(bal_us) >= int(prace[2]):
                q.execute("update ugc_users set balance = balance - " + str(prace[2]) + " where id = " + str(
                    call.from_user.id))
                connection.commit()
                tomorrow = datetime.now() + timedelta(days=30)
                tomorrow_formatted = tomorrow.strftime('%d/%m/%Y')
                q.execute(
                    f"update ugc_users set data = '{tomorrow_formatted}' where id = '{call.from_user.id}'")
                connection.commit()
                bot.send_message(call.message.chat.id, '''✔️ Подписка оформлена''', parse_mode='HTML',
                                 reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, '''✖️ Пополните баланс''', parse_mode='HTML',
                                 reply_markup=keyboard)

        if str(temp_id) == '3':
            if int(bal_us) >= int(prace[3]):
                q.execute("update ugc_users set balance = balance - " + str(prace[3]) + " where id = " + str(
                    call.from_user.id))
                connection.commit()
                tomorrow = datetime.now() + timedelta(days=90)
                tomorrow_formatted = tomorrow.strftime('%d/%m/%Y')
                q.execute(
                    f"update ugc_users set data = '{tomorrow_formatted}' where id = '{call.from_user.id}'")
                connection.commit()
                bot.send_message(call.message.chat.id, '''✔️ Подписка оформлена''', parse_mode='HTML',
                                 reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, '''✖️ Пополните баланс''', parse_mode='HTML',
                                 reply_markup=keyboard)

        if str(temp_id) == '4':
            if int(bal_us) >= int(prace[4]):
                q.execute("update ugc_users set balance = balance - " + str(prace[4]) + " where id = " + str(
                    call.from_user.id))
                connection.commit()
                tomorrow = datetime.now() + timedelta(days=999)
                tomorrow_formatted = tomorrow.strftime('%d/%m/%Y')
                q.execute(
                    f"update ugc_users set data = '{tomorrow_formatted}' where id = '{call.from_user.id}'")
                connection.commit()
                bot.send_message(call.message.chat.id, '''✔️ Подписка оформлена''', parse_mode='HTML',
                                 reply_markup=keyboard)
            else:
                bot.send_message(call.message.chat.id, '''✖️ Пополните баланс''', parse_mode='HTML',
                                 reply_markup=keyboard)

    elif call.data == 'info':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(f'SELECT COUNT(id) FROM akk')
        akkakk = q.fetchone()[0]

        q.execute(f'SELECT COUNT(id) FROM list_chat')
        chat = q.fetchone()[0]

        q.execute(f'SELECT SUM(colvo_send) FROM list_chat')
        colvo_send = q.fetchone()[0]

        q.execute(f'SELECT COUNT(id) FROM list_chat WHERE status = "Send"')
        chat_no_send = q.fetchone()[0]

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=f'''💢 Как работает сервис ?!''',
                                                url=f'https://telegra.ph/Informaciya-po-proektu-10-06'),
                     types.InlineKeyboardButton(text=f'''🧑‍🔧 Задать вопрос''', url=f'https://t.me/ADM_ROCKET'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''🪧 База чатов''', callback_data=f'База'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.message.chat.id, f'''📖 Подробная информация по боту:
▪️ https://telegra.ph/Informaciya-po-proektu-10-06

📊 Общая статистика бота:
▪️Аккаунтов: {akkakk}
▪️Чатов: {chat}
▪️Отправлено: {colvo_send}
▪️Очередь отправки: {chat_no_send}''', parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)

    elif call.data[:17] == 'admin_search_user':
        msg = bot.send_message(call.message.chat.id, f'<b>Введи id пользователя</b>', parse_mode='HTML',
                               reply_markup=keyboards.otmena)
        bot.register_next_step_handler(msg, searchuser)

    elif call.data[:17] == 'admin_search_chat':
        msg = bot.send_message(call.message.chat.id, f'<b>Введи номер аккаунта</b>', parse_mode='HTML',
                               reply_markup=keyboards.otmena)
        bot.register_next_step_handler(msg, searchchat)

    elif call.data[:17] == 'del_akkss':
        msg = bot.send_message(call.message.chat.id, f'<b>Введи номер аккаунта для удаления</b>', parse_mode='HTML',
                               reply_markup=keyboards.otmena)
        bot.register_next_step_handler(msg, delakks)

    elif call.data[:15] == 'добавитьбаланс_':
        global id_user_edit_bal1
        id_user_edit_bal1 = call.data[15:]
        msg = bot.send_message(call.message.chat.id,
                               'Введи сумму: ', parse_mode='HTML')
        bot.register_next_step_handler(msg, add_money2)

    if call.data == 'База':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        q.execute(
            f"SELECT data FROM ugc_users where id = '{call.message.chat.id}'")
        datas = q.fetchone()[0]
        if str(datas) != str('Нет'):
            code = call.message.chat.id
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'info'))
            doc = open('chat.rar', 'rb')
            bot.send_document(call.message.chat.id, doc, caption='✔️ Спасибо за скачивание чатов.',
                              reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                text=f'''⬅️ Назад''', callback_data=f'info'))
            bot.send_message(call.from_user.id,
                             f'''✖️ Доступно только с подпиской и влючает базу из более чем 100,000 чатов !''',
                             parse_mode='HTML', reply_markup=keyboard)

    elif call.data == 'конкурс':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'top_ref'))
        bot.send_message(call.message.chat.id, f'''🎁 Каждое первое число месяца, мы будет выдавать по бесплатной подписке топ 3 партнёров.

▫️ За накрутку рефералов вы будите получать блокировку без возможности использования и возврата средств.''',
                         parse_mode='HTML', reply_markup=keyboard)

    elif call.data == 'top_ref':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        text = f"<b>🏆Топ партнеров:\n\n</b>"
        q.execute(f'SELECT * FROM ugc_users ORDER BY ref_colvo DESC')
        rows = q.fetchall()
        premium = ['🥇', '🥈', '🥉', '🏅', '🏅']
        l = len(rows)
        if l > 10:
            l = 10
        for i in range(l):
            if i <= len(premium) - 1:
                userid = int(rows[i][0])
                try:
                    UsrInfo = bot.get_chat_member(userid, userid).user
                    text += f"{premium[i]}{i + 1}) @{UsrInfo.username} | {rows[i][9]} реферал(ов)\n"
                except Exception as e:
                    text += f"{premium[i]}{i + 1}) @None | {rows[i][9]} реферал(ов)\n"
            else:
                try:
                    userid = int(rows[i][0])
                    UsrInfo = bot.get_chat_member(userid, userid).user
                    text += f"🎗{i + 1}) @{UsrInfo.username} | {rows[i][9]} реферал(ов)\n"
                except Exception as e:
                    text += f"🎗{i + 1}) @None | {rows[i][9]} реферал(ов)\n"
        keyboard = types.InlineKeyboardMarkup()
        # keyboard.add(types.InlineKeyboardButton(text=f'''🎁 Конкурс партнеров''',callback_data=f'конкурс'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'ref'))
        bot.send_message(call.message.chat.id,
                         f'''{text}''', parse_mode='HTML', reply_markup=keyboard)

    elif call.data == 'сменапрайса':
        msg = bot.send_message(call.message.chat.id, f'Укажите цены с новой строки 4 шт в порядке возрастания',
                               parse_mode='HTML', reply_markup=keyboards.otmena)
        bot.register_next_step_handler(msg, smena_prace)

    elif call.data == 'рекламачата':
        connection = connect(host=config.bd_host, user=config.bd_login, password=config.bd_pass,
                             database=config.bd_base)
        q = connection.cursor()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(text=f'''🚀 Вступить в чат''', url=f'https://t.me/joinchat/qurKRfvUjq1iMmFi'))
        keyboard.add(types.InlineKeyboardButton(
            text=f'''⬅️ Назад''', callback_data=f'Главное'))
        bot.send_message(call.message.chat.id, 'Начинаем отправлять!')
        q.execute("SELECT * FROM ugc_users")
        row = q.fetchall()
        for i in row:
            time.sleep(0.3)
            try:
                bot.send_message(i[0],
                                 f'''💢 Вступайте в чат и обсуждайте все обновления бота и предлагайте свой идей !''',
                                 parse_mode='HTML', reply_markup=keyboard)
            except:
                pass
        bot.send_message(call.message.chat.id, 'Готово | /admin')


bot.polling(True)
