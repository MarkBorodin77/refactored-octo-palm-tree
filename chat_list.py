import asyncio
from telethon import TelegramClient
from telethon.errors import rpcerrorlist
from datetime import date, datetime
import re
import config
from getpass import getpass
from mysql.connector import connect, Error

api_id = 988074
api_hash = "a5ec8b7b6dbeedc2514ca7e4ba200c13"




async def get_chats(phone,users):
	try:
		connection = connect(host=config.bd_host,user=config.bd_login,password=config.bd_pass,database=config.bd_base)
		q = connection.cursor()
		q.execute(f'SELECT proxi FROM akk where id =  "{phone}"')
		proxi = q.fetchone()[0]
		login_prox = proxi.split('@')[0].split(':')[0]
		pass_prox = proxi.split('@')[0].split(':')[1]
		ip_prox = proxi.split('@')[1].split(':')[0]
		port_prox = proxi.split('@')[1].split(':')[1]
		proxy = {'proxy_type':'socks5','addr': str(ip_prox),'port': int(port_prox),'username':str(login_prox),'password': str(pass_prox),'rdns': True}
		connection = connect(host=config.bd_host,user=config.bd_login,password=config.bd_pass,database=config.bd_base)
		q = connection.cursor()
		print(phone)
		client = TelegramClient(str(phone), api_id, api_hash, device_model="Ids bot", system_version="6.12.0", app_version="10 P (28)", proxy=proxy)
		await client.connect()
		me = await client.get_me()
		dialogs = await client.get_dialogs()
		for chat in dialogs:
			try:
				print(chat.entity.megagroup)
				if chat.entity.megagroup ==  True:
					q.execute(f"SELECT * FROM list_chat WHERE akk = '{phone}' and id = '{chat.id}'")
					row = q.fetchone()
					if row is None:
						try:
							q.execute("INSERT INTO list_chat (id,name,akk,id_user,status) VALUES ('%s','%s','%s','%s','%s')"%(chat.id,chat.name,phone,users,'NoSend'))
							connection.commit()
						except Exception as e:
							pass
			except:
				pass

		try:
			await client.disconnect()
		except OSError:
			return 'ddddd'
			print('Error on disconnect')
		return 'ok'

	except Exception as e:
		print(e)
		try:
			await client.disconnect()
		except OSError:
			return 'ddddd'



def mainssssss(phone,users):
	try:
		www = loop.run_until_complete(get_chats(phone,users))
		return www
	except Exception as e:
		return 'ddddd'

loop = asyncio.get_event_loop()