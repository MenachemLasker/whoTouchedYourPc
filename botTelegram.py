import telebot
import os
import json
from usersManger import *

BOT_TOKEN = ''
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "/follow or /unfollow")


@bot.message_handler(commands=['follow'])
def handle_follow(message):
    msg = bot.reply_to(message, "אנא הזן שם משתמש:")
    bot.register_next_step_handler(msg, get_username_step)


@bot.message_handler(commands=['unfollow'])
def handle_unfollow(message):
    msg = bot.reply_to(message, "אנא הזן שם משתמש:")
    bot.register_next_step_handler(msg, unfollow)


def get_username_step(message):
    chat_id = message.chat.id
    username = message.text
    if has_user(username):
        if he_follow(chat_id, username):
            bot.send_message(chat_id, f"אתה כבר עוקב אחרי {username}.")
        else:
            msg = bot.reply_to(message, "אנא הזן סיסמה:")
            bot.register_next_step_handler(msg, password_step, username)
    else:
        msg = bot.reply_to(message, "שם המשתמש לא קיים, אנא נסה שוב:")
        bot.register_next_step_handler(msg, get_username_step)


def password_step(message, username):
    chat_id = message.chat.id
    password = message.text
    print(hash_sha256(password))
    if verify_user(username, password):
        follow_user(username, chat_id)
    else:
        bot.send_message(chat_id, "הסיסמה שגויה")


def unfollow(message):
    chat_id = message.chat.id
    username = message.text
    if he_follow(chat_id, username):
        unfollow_user(username, chat_id)

    else:
        msg = bot.reply_to(message, "שם המשתמש לא קיים, אנא נסה שוב:")
        bot.register_next_step_handler(msg, unfollow)


def follow_user(username, chat_id):
    file_path = ('user_chat_ids.json')
    if not has_followrs(username):
        new_user_chat_ids = {
            username: [chat_id]
        }
        if os.path.isfile(file_path):
            with open(file_path, 'r') as infile:
                user_chat_ids = json.load(infile)
            user_chat_ids.update(user_chat_ids)
        else:
            user_chat_ids = new_user_chat_ids
    else:
        with open(file_path, 'r') as infile:
            user_chat_ids = json.load(infile)
            user_chat_ids[username].append(chat_id)
    with open(file_path, 'w') as outfile:
        json.dump(user_chat_ids, outfile)
    print(f"Data added to {file_path}")
    bot.send_message(chat_id, f"אתה עכשיו עוקב אחרי {username}.")


def unfollow_user(username, chat_id):
    file_path = ('user_chat_ids.json')
    if not has_followrs(username):
        return False
    else:
        with open(file_path, 'r') as infile:
            user_chat_ids = json.load(infile)
            user_chat_ids[username].remove(chat_id)
        with open(file_path, 'w') as outfile:
            json.dump(user_chat_ids, outfile)
            bot.send_message(chat_id, f"אתה עכשיו לא עוקב אחרי {username}.")
        return True


def start_bot():
    bot.polling()
