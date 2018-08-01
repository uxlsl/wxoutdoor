import datetime
import logging
import fire
import requests
import pymongo
import wechatsogou


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='outdoor.log',
        level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)


client = pymongo.MongoClient()
outdoor_db = client.outdoor
ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=10)



class outDoor(object):
    def update_outdoor_gzh(self):
        """
        更新户外公众号
        """
        for page in range(1, 11):
            gzhs = ws_api.search_gzh('广州 户外', page=page)
            for gzh in gzhs:
                outdoor_db.gzh.update(
                        {'wechat_id':gzh['wechat_id']},
                        gzh, upsert=True)
                logging.debug(gzh)

    def update_outdoor_article(self):
        """
        更新户外活动信息
        """
        for gzh in list(outdoor_db.gzh.find()):
            results = ws_api.get_gzh_article_by_history(gzh['wechat_name'])
            for art in results['article']:
                logging.debug(art)
                art['wechat_name'] = gzh['wechat_name']
                art['wechat_id'] = gzh['wechat_id']
                outdoor_db.article.update(
                        {'fileid':art['fileid']},
                        art,upsert=True)

    def handle_outdoor_article(self):
        """
        处理文章一些数据
        """
        for art in list(outdoor_db.article.find()):
            art['created_at'] = datetime.datetime.fromtimestamp(
                    art['datetime'])
            outdoor_db.article.update(
                    {'fileid':art['fileid']},
                    art,upsert=True)


    def update_outdoor_article_content(self):
        """
        更新户外信息内容
        """
        for art in list(outdoor_db.article.find()):
            logging.debug('更新 {}'.format(art['title']))
            try:
                r = requests.get(art['content_url'], timeout=60)
                art['content'] = r.text
                outdoor_db.article.update(
                        {'fileid':art['fileid']},
                        art,upsert=True)
            except:
                logging.error('无法更新 {}'.format(art['title']))


if __name__ == '__main__':
    fire.Fire(outDoor)
