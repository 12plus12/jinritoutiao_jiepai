import requests
import re
import pymongo
import os
import time
from hashlib import md5
from urllib.parse import urlencode
from multiprocessing import Pool


def pic_spider(offset):
    """发起ajax请求，返回数据"""
    base_url = 'https://www.toutiao.com/search_content/?'

    headers = {
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    parmas = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery',
    }

    url = base_url + urlencode(parmas, encoding='utf-8')

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(e.args)


def parse_tool(items):
    """解析数据，提取标题和图片"""
    items = items.get('data')

    for item in items:
        # 字典用来保存需要的数据
        pic_floder = dict()
        pic_floder['title'] = item.get('title')
        pic_floder['author'] = item.get('media_name')
        pic_floder['author_id'] = item.get('media_creator_id')
        pic_floder['article_url'] = item.get('article_url')

        small_image_list = item.get('image_list')
        for i, small_image in enumerate(small_image_list):
            pic_floder['pic_{}'.format(i+1)] = 'http:' + re.sub("list", 'large', small_image.get('url'))

        yield pic_floder


def save_to_mongodb(floder, collection):
    """保存到mongodb"""
    collection.insert(floder)


def save_to_floder(floder):
    """按title文件夹名保存图片"""
    # 当前文件夹中不存在才新建文件夹
    title = floder.get('title')
    if title not in os.listdir('./pic/'):
        os.mkdir('./pic/{}'.format(title))

        for key, value in floder.items():
            if key.startswith('pic_'):
                response = requests.get(value)
                if response.status_code == 200:
                    file_path = './pic/{0}/{1}.jpg'.format(title, md5(response.content).hexdigest())
                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as f:
                            f.write(response.content)


def main(offset):
    items = pic_spider(offset)

    # 连接mongodb
    # client = pymongo.MongoClient(host='192.168.0.104', port=27017)
    # collection = client['jinritoutiao']['jiepai']

    for floder in parse_tool(items):
        save_to_floder(floder)
        # time.sleep(1)


if __name__ == '__main__':
    pool = Pool()

    GROUP_START = 0
    GROUP_END = 20

    groups = [x * 10 for x in range(GROUP_START, GROUP_END+1)]

    pool.map(main, groups)
    pool.close()
    pool.join()

    print('DONE')