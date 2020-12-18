#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
# Coded with ❤️ by Neranjana Prasad (@NandiyaLive)


from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import sys
import shutil
import glob
import os
import zipfile
import pathlib
import telegram
from telegram import Bot
import requests
from reddit import request_reddit

bot_token = ""


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="This bot can help you to download photos & videos from subreddits using subreddit name without leaving Telegram.\nPlease read /help before use.", parse_mode=telegram.ParseMode.HTML)


def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Simply send  <code>/get <subreddit name></code>.\n\n<b>How to find the subreddit name?</b>\nYou can find it in the browser's Address bar.\n<b>Example : </b>Subreddit name of https://www.reddit.com/r/gameofthrones is 'gameofthrones'.", parse_mode=telegram.ParseMode.HTML)


def about(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='''Made with ❤️ + python-telegram-bot & <a href="https://github.com/thisisppn/reddit-media-downloader">reddit-media-downloader</a> by @NandiyaLive.\nSource Code : <a href="https://github.com/NandiyaLive/RedditDLBot">GitHub</a>\nPlease contact me on @NandiyaThings Support Chat.In case you want to PM please use @NandiyaBot.''', parse_mode=telegram.ParseMode.HTML)


def echo(update, context):
    update.message.reply_text(
        "You have to send a command with an username.\nRead /help before use.")


@run_async
def get(update, context):

    sub_reddit = update.message.text.replace("/get ", "")

    chat_id = update.message.chat_id

    sorting = 'top'
    if sorting == 'top':
        url = 'https://www.reddit.com/r/{0}/top.json?sort=top&t=all'.format(
            sub_reddit)
    else:
        url = 'https://www.reddit.com/r/{0}/.json?'.format(sub_reddit)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Cooking your request 👨‍🍳\nThis may take longer, take a nap I can handle this without you.", parse_mode=telegram.ParseMode.HTML)

    request_reddit(url, chat_id, sub_reddit)


def upload(file_path, chat_id, sub_reddit):
    bot = Bot(token=bot_token)

    bot.send_message(chat_id, text="Download Completed.\n🗄 Archiving files...")

    zf = zipfile.ZipFile(f"{sub_reddit}.zip", "w")
    for dirname, files in os.walk(sub_reddit):
        zf.write(sub_reddit)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

    bot.send_message(chat_id, text="Uploading to Telegram...")

    for zip_file in glob.glob("*.zip"):
        bot.send_document(chat_id, document=open(zip_file, 'rb'))

    try:
        shutil.rmtree(sub_reddit)
        os.remove(f"{sub_reddit}.zip")
    except Exception:
        pass


def main():
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, run_async=True))
    dp.add_handler(CommandHandler("get", get, run_async=True))
    dp.add_handler(CommandHandler("help", help, run_async=True))
    dp.add_handler(CommandHandler("about", about, run_async=True))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
