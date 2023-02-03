import telebot
import datetime
from telebot import types, apihelper
import sqlite3
import datetime
import time
from datetime import datetime, timedelta
import re
import config
from getpass import getpass
from mysql.connector import connect, Error

bot = telebot.TeleBot(config.bot_logi_token)
bot2 = telebot.TeleBot(config.bot_osnova_token)
while True:
	try:
		connection = connect(host=config.bd_host,user=config.bd_login,password=config.bd_pass,database=config.bd_base)
		q = connection.cursor()
		clock_in_half_hour = datetime.now()
		q.execute(f"SELECT * FROM list_chat where time_step = '{clock_in_half_hour.hour}:{clock_in_half_hour.minute}'")
		row = q.fetchall()
		for i in row:
			try:
				clock_in_half_hour = datetime.now() + timedelta(minutes=(int(i[4])))
				q.execute(f"update list_chat set time_step = '{clock_in_half_hour.hour}:{clock_in_half_hour.minute}' where id_str = '{i[0]}'")
				connection.commit()
				q.execute(f"update list_chat set status = 'Send' where id_str = '{i[0]}'")
				connection.commit()
			except Exception as e:
				q.execute(f"DELETE FROM list_chat where id_str = '{i[0]}'")
				connection.commit()
				
		tomorrow = datetime.now()
		tomorrow_formatted = tomorrow.strftime('%d/%m/%Y')
		q.execute(f"SELECT * FROM ugc_users where data = '{tomorrow_formatted}'")
		row = q.fetchall()
		for i in row:
			q.execute(f"update ugc_users set data = 'Нет' where id = '{i[0]}'")
			connection.commit()
			q.execute(f"update list_chat set time_step = 'None' where id_user = '{i[0]}'")
			connection.commit()
			bot2.send_message(i[0], '❌ Ваша подписка истекла, автопостинг приостановлен.')

	except Exception as e:
		bot.send_message(config.chat_logi_error, f'❓ Ошибка time setup: {e} ❓')
