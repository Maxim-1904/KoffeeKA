import config
import telebot as tb
from telebot import types
from telebot.types import Message, BotCommand
import sqlite3
import QR_gen


bot = tb.TeleBot(config.token)
CODE = "1234"

# Создаем подключение к базе данных
conn = sqlite3.connect('coffeebot.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения данных пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                stamps INTEGER DEFAULT 0,
                free_coffee BOOLEAN DEFAULT FALSE)''')
conn.commit()

def keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Узнать баланс")
    markup.add(btn1)
    return markup

def get_stamp(user_id: int) -> int:
    cursor.execute("SELECT stamps FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def set_stamps(user_id: int, stamps: int):
    if get_stamp(user_id) == 0:
        cursor.execute("INSERT INTO users(user_id, stamps) VALUES(?, ?)", (user_id, stamps))
    else:
        cursor.execute("UPDATE users SET stamps = ? WHERE user_id = ?", (stamps, user_id))
        

    

@bot.message_handler(commands=["start"])
def start(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) == 2 and parts[1] == "get_stamp":
        stamps_status(message)
    else:
        bot.send_message(message.chat.id, 
                        "Привет, я бот для накопительной системы заведения КОФЕЙКА",
                        reply_markup=keyboard())
    
    # Проверяем существование пользователя в БД
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()



msg1 = None
@bot.message_handler(commands=["get_stamp"])
def stamps_status(message):
    user_id = message.from_user.id
    last_message = []
    global msg1
    # Проверяем, есть ли пользователь в БД
    cursor.execute("SELECT stamps FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        # Если пользователя нет, создаем запись
        cursor.execute("INSERT INTO users (user_id, stamps) VALUES (?, 1)", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Печать получена. Спасибо за покупку!")
        return
    
    stamps = row[0] + 1
    
    if stamps == 10:
        cursor.execute("UPDATE users SET stamps = 10, free_coffee = TRUE WHERE user_id = ?", (user_id,))
        conn.commit()
        msg1 = bot.send_message(message.chat.id, 
                        "Печать получена. Спасибо за покупку! Вы получили 10 печатей. "
                        "Вам полагается бесплатный кофе. Покажите это сообщение на кассе и отсканируйте QR-код для его получения."
                        "(При следующей покупке это сообщение исчезнет.)")
        # last_message.extend([msg1.message_id])
    elif stamps >= 11:
        cursor.execute("UPDATE users SET stamps = 0, free_coffee = FALSE WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Бесплатный кофе получен.")
        bot.delete_message(message.chat.id, msg1.message_id)
    else:
        cursor.execute("UPDATE users SET stamps = ? WHERE user_id = ?", (stamps, user_id))
        conn.commit() 
        bot.send_message(message.chat.id, "Печать получена. Спасибо за покупку!")



@bot.message_handler(func=lambda message: message.text == "Узнать баланс")
def handle_balance(message):
    user_id = message.from_user.id
    cursor.execute(
        "SELECT stamps, free_coffee FROM users WHERE user_id = ?", 
        (user_id,)
    )
    stamps, free_coffee = cursor.fetchone()
    
    response = f"У вас {stamps} печатей."
    
    bot.send_message(message.chat.id, response)


    
bot.infinity_polling()