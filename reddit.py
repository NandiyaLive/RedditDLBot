#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests as r
from urllib.request import urlretrieve
import os
import time
import sys
import argparse
from bot import upload

headers = \
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}


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
