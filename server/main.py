import pymongo
import wechatsogou


client = pymongo.MongoClient()
outdoor_db = client.outdoor
ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=10)


def update_outdoor_gzh():
    """
    更新公众号
    """
    for page in range(1, 11):
        gzhs = ws_api.search_gzh('广州 户外', page=page)
        for gzh in gzhs:
            outdoor_db.gzh.update(
                    {'wechat_id':gzh['wechat_id']},
                    gzh, upsert=True)


def update_outdoor_article():
    """
    更新文章
    """
    for gzh in list(outdoor_db.gzh.find()):
        print(gzh)
        results = ws_api.get_gzh_article_by_history(gzh['wechat_name'])
        for art in results['article']:
            art['wechat_name'] = gzh['wechat_name']
            art['wechat_id'] = gzh['wechat_id']
            outdoor_db.article.update(
                    {'fileid':art['fileid']},
                    art,upsert=True)


