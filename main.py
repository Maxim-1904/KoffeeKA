import config
import telebot as tb
from telebot import types
bot = tb.TeleBot(config.token)
users_db = {}
CODE = "1234"

def keyboard():
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_print_btn = types.InlineKeyboardButton("Получить печать", callback_data="get_print")
    get_balanse_btn = types.InlineKeyboardButton("Узнать баланс", callback_data="get_balanse")
    reply_markup.add(get_print_btn, get_balanse_btn)


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id,
        "Привет, я бот для накопительной системы заведения КОФЕЙКА",reply_markup=keyboard())
    if user_id not in users_db:
        users_db[user_id] = {'stamps': 0,'free_coffee': False}


@bot.message_handler(func=lambda message: message.text == "Узнать баланс")
def handle_balance(message):
    user_id = message.from_user.id
    stamps = users_db[user_id]['stamps']
    if users_db[user_id]['free_coffee']:
        bot.send_message(message.chat.id,f"У вас {stamps} печатей. У вас есть бесплатное кофе! Покажите это сообщение на кассе. (При следующей покупке это сообщение исчезнет.)")
    else:
        bot.send_message(message.chat.id, f"У вас {stamps} печатей.")

@bot.message_handler(func=lambda message: message.text == "Получить печать")
def get_stamp(message):
    user_id = message.from_user.id
    if users_db[user_id]['free_coffee']:
        users_db[user_id]['free_coffee'] = False
        bot.send_message(message.chat.id,"Сообщение о бесплатном кофе удалено.")
    mesege = bot.send_message(message.chat.id, "Введите код для подтверждения оплаты")
    bot.register_next_step_handler(mesege, chek_code())

def chek_code(message):
    user_id = message.from_user.id
    user_code = message.text
    if user_code == CODE:
        users_db[user_id]['stamps'] += 1
        if users_db[user_id]['stamps'] >= 10:
            users_db[user_id]['stamps'] = 0
            users_db[user_id]['free_coffee'] = True
            bot.send_message(message.chat.id,"Печать получена. Спасибо за покупку! Вы получили 10 печатей. Вам полагается бесплатное кофе. Покажите это сообщение на кассе, чтобы вам его одобрили. (При следующей покупке сообщение удалится)")
        else:
            bot.send_message(message.chat.id, "Печать получена. Спасибо за покупку!")
        bot.send_message(message.chat.id,"Что вы хотите сделать?",reply_markup=keyboard())
    elif user_code != CODE:
        bot.send_message(message.chat.id, "Код введён неверно")
        bot.send_message(message.chat.id,"Что вы хотите сделать?",reply_markup=keyboard())


bot.infinity_polling()
