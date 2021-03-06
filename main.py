#from flask import message_flashed
import telebot
from telebot import types
import psycopg2
from aiogram.dispatcher.filters import Command
from aiogram.types import Message
#import os
#from flask import Flask, request
#from gevent.pywsgi import WSGIServer

name = ''
room = ''
problem = ''
admin_id = 764597745;

TOKEN = '5270219842:AAG8kGXwlksrezWfFQ7AEK44gklFlROolf0'
APP_URL = f'https://hostelsservices.herokuapp.com/{TOKEN}'
#app = Flask(__name__)
DB_URI = 'postgres://iehhfwgdwknoic:598e9af534ea9047fcdd496a97f0c35a8b2ce2bb9da8f72c4be72d5897a90a0f@ec2-176-34-211-0.eu-west-1.compute.amazonaws.com:5432/d4ce89bq7rae1k'

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, 'Напишите Имя')
    bot.register_next_step_handler(message, reg_name)

    global id
    id = message.from_user.id
    username = message.from_user.username

    db_object.execute(f"SELECT id FROM users WHERE id = {id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users (id, usersname, name, room, type, message) VALUES (%s, %s, %s, %s, %s, %s)",
                          (id, username, 0, 0, 0, 0))
        db_connection.commit()



def reg_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Напишите Номер комнаты')
    bot.register_next_step_handler(message, reg_room)

    db_object.execute(f"UPDATE users SET name = '{name}' WHERE id = '{id}';")
    db_connection.commit()

def reg_room(message):
    global room
    room = message.text
    while room == 0:
        try:
            room = int(message.text)
        except Exception:
            bot.send_message(message.from_user.id, "Вводите цифрами!")


    db_object.execute(f"UPDATE users SET room = '{room}' WHERE id = '{id}';")
    db_connection.commit()

    keyboard = types.InlineKeyboardMarkup()
    key_plumber = types.InlineKeyboardButton(text='Сантехник', callback_data='plumber')
    keyboard.add(key_plumber)
    key_carpenter = types.InlineKeyboardButton(text='Плотник', callback_data='carpenter')
    keyboard.add(key_carpenter)
    key_provider = types.InlineKeyboardButton(text='Провайдер', callback_data='provider')
    keyboard.add(key_provider)
    bot.send_message(message.from_user.id, name + ', выберите услугу:', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "plumber":
        bot.send_message(call.message.chat.id, "Опишите проблему")
        bot.register_next_step_handler(call.message, reg_problem)

        db_object.execute(f"UPDATE users SET type = '{'Сантехник'}' WHERE id = '{id}';")
        db_connection.commit()

    if call.data == "carpenter":
        bot.send_message(call.message.chat.id, "Опишите проблему")
        bot.register_next_step_handler(call.message, reg_problem)

        db_object.execute(f"UPDATE users SET type = '{'Плотник'}' WHERE id = '{id}';")
        db_connection.commit()


    elif call.data == "provider":
        bot.send_message(call.message.chat.id, "Опишите проблему")
        bot.register_next_step_handler(call.message, reg_problem)

        db_object.execute(f"UPDATE users SET type = '{'Провайдер'}' WHERE id = '{id}';")
        db_connection.commit()

def reg_problem(message):
    global problem
    problem = message.text
    bot.send_message(message.from_user.id, 'Заявка принята')

    db_object.execute(f"UPDATE users SET message = '{problem}' WHERE id = '{id}';")
    db_connection.commit()

@bot.message_handler(Command('sendall'))
async def send_all(message: Message):
    if message.chat.id == admin_id:
        await message.answer('Start')
        for i in db_object.users.id:
            await bot.send_message(i, message.text[message.text.find(' '):])

        await message.answer('Done')
    else:
        await message.answer('Error')

'''@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.pocess_new_updates([update])
    return '!', 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200

if __name__ == '__main__':
    #server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()'''

bot.infinity_polling()