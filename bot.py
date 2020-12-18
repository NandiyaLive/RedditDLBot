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


bot_token = ""
headers = \
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="This bot can help you to download photos & videos from subreddits using subreddit name without leaving Telegram.\nPlease read /help before use.", parse_mode=telegram.ParseMode.HTML)


def help(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Simply send  <code>/get [subreddit name]</code>.\n\n<b>How to find the subreddit name?</b>\nYou can find it in the browser's Address bar.\n<b>Example : </b>Subreddit name of https://www.reddit.com/r/gameofthrones is 'gameofthrones'.", parse_mode=telegram.ParseMode.HTML)


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


def get_gfycat_url(gfycat_name):
    gfycat = 'https://gfycat.com/cajax/get/{0}'
    
    response = r.get(gfycat.format(gfycat_name), headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        mp4url = response_json['gfyItem']['mp4Url']
        return mp4url
    else:
        return False


def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write('\r...%d%%, %d MB, %d KB/s, %d seconds passed'
                     % (percent, progress_size / (1024 * 1024), speed,
                        duration))
    sys.stdout.flush()


def download_media(
    img_url,
    file_name,
    source,
    folder_name,
    chat_id,
    sub_reddit
):
    try:
        file_path = folder_name
        if not os.path.exists(file_path):
            print('???', file_path, '????????')
            os.makedirs(file_path)

        if source == 'gfycat.com':
            gfycat_name = img_url.split('/')[-1]
            img_url = get_gfycat_url(gfycat_name)
            if img_url:
                file_suffix = os.path.splitext(img_url)[1]
                filename = '{}{}{}{}'.format(file_path, os.sep,
                                             file_name, file_suffix)
                if os.path.exists(filename):
                    print('File {0} already exists'.format(filename))
                    return False
                print('\nDownloading gfycat', img_url)
                urlretrieve(img_url, filename, reporthook)
        elif source == 'i.imgur.com':
            img_url = img_url.replace('.gifv', '.mp4')
            file_suffix = os.path.splitext(img_url)[1]
            filename = '{}{}{}{}'.format(file_path, os.sep, file_name,
                                         file_suffix)
            if os.path.exists(filename):
                print('File {0} already exists'.format(filename))
                return False
            print('\nDownloading imgur', img_url)
            urlretrieve(img_url, filename, reporthook)
        elif source == 'i.redd.it':
            file_suffix = os.path.splitext(img_url)[1]
            filename = '{}{}{}{}'.format(file_path, os.sep, file_name,
                                         file_suffix)
            if os.path.exists(filename):
                print('File {0} already exists'.format(filename))
                return False
            print('\nDownloading imgur', img_url)
            urlretrieve(img_url, filename, reporthook)

        upload(file_path, chat_id, sub_reddit)

    except Exception as e:
        print(e)


def request_reddit(url, chat_id, sub_reddit):
    response = r.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        next_page = response_json['data']['after']
        posts = response_json['data']['children']
        for post in posts:

            source = post['data']['domain']
            media_url = post['data']['url']
            filename = post['data']['title']
            download_media(media_url, filename.replace('/', '_'),
                           source, 'downloads', chat_id, sub_reddit)

        if next_page is not None:
            print('Heading over to next page ... ')
            url = url + '&after=' + next_page
            request_reddit(url, chat_id, sub_reddit)

    else:
        print(response)


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
