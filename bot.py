#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Coded with ❤️ by Neranjana Prasad (@NandiyaLive)


from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
import sys
import shutil
import glob
import os
import telegram
import requests
from reddit import request_reddit

bot_token = os.environ.get("BOT_TOKEN", "")


def start(update, context):
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="<b>Hi There! 👋</b>\nI can download photos & videos using subreddit name.\nPlease read /help before use.", parse_mode=telegram.ParseMode.HTML)


def help_command(update, context):
    """Send a message when the command /help is issued."""
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="This bot can help you to download photos & videos from subreddits using subreddit name without leaving Telegram. Simply send a <code>/get <subreddit name></code>.\n\n<b>How to find the subreddit name?</b>\nYou can find it in the browser's Address bar.\n<b>Example : </b>Subreddit name of https://www.reddit.com/r/gameofthrones is 'gameofthrones'.", parse_mode=telegram.ParseMode.HTML)


def about_command(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text='''Made with ❤️ + python-telegram-bot & reddit-media-downloader.\nSource Code : <a href="https://github.com/NandiyaLive/RedditDLBot">GitHub</a>''', parse_mode=telegram.ParseMode.HTML)


def contact_command(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Please contact me on @NandiyaX Chat.In case you want to PM please use @NandiyaBot.", parse_mode=telegram.ParseMode.HTML)


def echo(update, context):
    update.message.reply_text(
        "You have to send a command with an username.\nRead /help before use.")


@run_async
def get_command(update, context):

    msg = update.message.text.replace("/get ", "")

    sub_reddit = update.message.text.replace("/get ", "")
    sorting = 'top'
    if sorting == 'top':
        url = 'https://www.reddit.com/r/{0}/top.json?sort=top&t=all'.format(
            sub_reddit)
    else:
        url = 'https://www.reddit.com/r/{0}/.json?'.format(sub_reddit)

    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Cooking your request 👨‍🍳\nThis may take longer, take a nap I can handle this without you.", parse_mode=telegram.ParseMode.HTML)

    request_reddit(url)

    src_dir = "/downloads/" + msg
    for jpgfile in glob.iglob(os.path.join(src_dir, "*.jpg")):
        context.bot.send_photo(
            chat_id=update.message.chat_id, photo=open(jpgfile, 'rb'))

    for vidfile in glob.iglob(os.path.join(src_dir, "*.mp4")):
        context.bot.send_video(
            chat_id=update.message.chat_id, video=open(vidfile, 'rb'))

    try:
        shutil.rmtree(msg)
    except Exception:
        pass


def main():
    """Start the bot."""
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get", get_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("contact", contact_command))
    dp.add_handler(CommandHandler("about", about_command))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


