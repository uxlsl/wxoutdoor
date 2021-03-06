import datetime
import logging
import re

import fire
import requests
import traceback

from conf import outdoor_db, ws_api
from utils import (extract_money, extract_time_from_content,
                   extract_time_from_title)


class outDoor(object):
    def update_outdoor_gzh(self):
        """
        更新户外公众号
        """
        for page in range(1, 11):
            gzhs = ws_api.search_gzh('广州 户外', page=page)
            for gzh in gzhs:
                outdoor_db.gzh.update(
                    {
                        'wechat_id': gzh['wechat_id']
                    }, gzh, upsert=True)
                logging.debug(gzh)

    def update_outdoor_article(self):
        """
        更新户外活动信息
        """
        for gzh in outdoor_db.gzh.find(no_cursor_timeout=True):
            if 'wechat_name' not in gzh:
                continue
            logging.info('正在更新公众号 {}'.format(gzh['wechat_name']))
            try:
                results = ws_api.get_gzh_article_by_history(gzh['wechat_name'])
            except requests.exceptions.ReadTimeout:
                logging.debug('请求超时')
                continue
            except Exception as e:
                logging.error(traceback.format_exc())
                continue
            for art in results['article']:
                logging.debug(art)
                art['wechat_name'] = gzh['wechat_name']
                art['wechat_id'] = gzh['wechat_id']
                outdoor_db.article.update(
                    {
                        'fileid': art['fileid']
                    }, art, upsert=True)

    def handle_outdoor_article(self):
        """
        处理文章一些数据
        """
        for art in outdoor_db.article.find(no_cursor_timeout=True):
            art['created_at'] = datetime.datetime.fromtimestamp(
                art['datetime'])
            if 'content' not in art:
                continue
            art['money'] = extract_money(art['content'])
            if art['money'] is None:
                logging.debug('{} {}:无法提取活动价'.format(art['title'],
                                                     art['fileid']))
            outdoor_db.article.update(
                {
                    'fileid': art['fileid']
                }, art, upsert=True)

    def update_outdoor_article_content(self):
        """
        更新户外信息内容
        """
        for art in outdoor_db.article.find({'content':{'$exists': False}},
                no_cursor_timeout=True):
            logging.debug('更新 {} {}'.format(art['title'], art['content_url']))
            try:
                r = requests.get(art['content_url'], timeout=60)
                art['content'] = r.text
                outdoor_db.article.update(
                    {
                        'fileid': art['fileid']
                    }, art, upsert=True)
            except:
                logging.error('无法更新 {}'.format(art['title']))

    def update_outdoor_article_time(self):
        for art in outdoor_db.article.find(no_cursor_timeout=True):
            if 'content' not in art:
                continue
            start_time = extract_time_from_title(art['title'], art['created_at']) \
                    or extract_time_from_content(art['content'])
            if start_time:
                art['start_time'] = start_time
                outdoor_db.article.update(
                    {
                        'fileid': art['fileid']
                    }, art, upsert=True)
            else:
                logging.debug('无法发现开始时间 {} {}'.format(art['title'],
                                                      art['content_url']))


if __name__ == '__main__':
    fire.Fire(outDoor)
