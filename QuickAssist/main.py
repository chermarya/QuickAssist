import telebot
import json
from config import TOKEN, ADMIN_IDS
from database import add_ticket, get_new_tickets, reply_to_ticket, get_user_id_by_ticket
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot(TOKEN)

with open("faq.json", encoding="utf-8-sig") as f:
    faq_dict = json.load(f)

user_modes = {}

def generate_faq_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for question in faq_dict:
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("⬅️ Назад"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def start_help(message):
    user_modes[message.from_user.id] = None
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(KeyboardButton("📚 FAQ"), KeyboardButton("👨‍💼 Допомога адміністратора"))
    bot.send_message(message.chat.id, "👋 Вітаємо! Оберіть опцію:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📚 FAQ")
def faq_menu(message):
    user_modes[message.from_user.id] = "faq"
    bot.send_message(message.chat.id, "Оберіть запитання:", reply_markup=generate_faq_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "👨‍💼 Допомога адміністратора")
def support_mode(message):
    user_modes[message.from_user.id] = "support"
    bot.send_message(message.chat.id, "✍️ Напишіть ваше питання, і ми його передамо адміністратору.")

@bot.message_handler(func=lambda msg: msg.text == "⬅️ Назад")
def back_to_menu(message):
    start_help(message)

@bot.message_handler(commands=['view_tickets'])
def view_tickets(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    tickets = get_new_tickets()
    if not tickets:
        bot.send_message(message.chat.id, "Немає нових звернень.")
        return
    for tid, user, msg in tickets:
        response = (
            f"📩 Нове звернення:\n"
            f"🆔 ID: {tid}\n"
            f"👤 Користувач: @{user if user else 'N/A'}\n"
            f"💬 Повідомлення: {msg}"
        )
        bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['reply'])
def reply(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        _, tid, *reply_text = message.text.split()
        tid = int(tid)
        reply_text = ' '.join(reply_text)
        user_id = get_user_id_by_ticket(tid)
        if not user_id:
            bot.send_message(message.chat.id, "❌ Звернення не знайдено.")
            return
        bot.send_message(user_id, f"💬 Відповідь адміністратора:\n{reply_text}")
        reply_to_ticket(tid, reply_text)
        bot.send_message(message.chat.id, "✅ Відповідь надіслано.")
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Формат: /reply <id> <текст>")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id
    mode = user_modes.get(user_id)

    if mode == "faq":
        answer = faq_dict.get(message.text)
        if answer:
            bot.send_message(message.chat.id, answer, reply_markup=generate_faq_keyboard())
        else:
            bot.send_message(message.chat.id, "❓ Таке питання не знайдено у базі.", reply_markup=generate_faq_keyboard())
    elif mode == "support":
        add_ticket(user_id, message.from_user.username, message.text)
        bot.send_message(message.chat.id, "✅ Ваше звернення прийнято! Очікуйте відповідь.")
    else:
        start_help(message)

bot.polling()
