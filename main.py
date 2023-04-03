import os
from urllib.parse import urlencode

import telebot
from pytube import YouTube
import requests

token = 'TOKEN'  # Your telegram bot token
google_api_token = 'google-api-token'  # It can be anything, it doesn't matter

bot = telebot.TeleBot(token)

users = []


def translate(text, language):
    global google_api_token
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=' \
          '{}&tl={}&dt=t&q={}&key={}'.format('en', language, urlencode({'q': text}).split('=')[-1], google_api_token)
    return ''.join([r[0] for r in requests.get(url).json()[0]])


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, translate(
        'Hi! With the help of this bot, you can download videos from YouTube. To receive a video, write its address '
        'and send it to me',
        message.from_user.language_code))


@bot.message_handler(content_types=['text'])
def download(message):
    if message.from_user.id not in users:
        mess = message.text.replace(' ', '')
        if not mess.startswith('https://'):
            mess = 'https://' + mess
        bot.send_message(message.chat.id,
                         translate('The download has started, please wait a bit...', message.from_user.language_code))
        try:
            users.append(message.from_user.id)
            video = YouTube(mess).streams.filter(progressive=True, file_extension='mp4').order_by(
                'resolution').desc().first().download()
            with open(video, 'rb') as v:
                bot.send_video(message.chat.id, v)
                os.remove(video)
            users.remove(message.from_user.id)
        except Exception:
            os.remove(video)
            users.remove(message.from_user.id)
            bot.send_message(message.chat.id,
                             translate('Sorry, but there is no such video on YouTube', message.from_user.language_code))
    else:
        bot.send_message(message.chat.id, translate("Sorry, but you'll have to wait for the previous video to load",
                                                    message.from_user.language_code))


bot.polling(none_stop=True)
