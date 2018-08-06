import datetime
import re

import html2text

from conf import outdoor_db
from bson.son import SON

HT = html2text.HTML2Text()


def get_first_not_none(lst, v=None):
    return next((item for item in lst if item is not None), v)


def extract_time_from_title(text, ref_time=None):
    """
    提取第一个时间
    """
    if ref_time is None:
        ref_time = datetime.datetime.now()
    m = re.search((r'(?P<month1>\d{1,2})月(?P<day1>\d{1,2})'
                   r'|(?P<year2>\d{4})\.(?P<month2>\d{1,2})\.(?P<day2>\d{1,2})'
                   r'|(?P<year3>\d{4})年【(?P<month3>\d{1,2})\.(?P<day3>\d{1,2})'
                   r'|(?P<year4>\d{4})年(?P<month4>\d{1,2})月(?P<day4>\d{1,2})'
                   r'|(?P<month5>\d{1,2})\.(?P<day5>\d{1,2})'), text)
    if m:
        d = m.groupdict()
        year = get_first_not_none(
            (d.get('year{}'.format(i)) for i in range(1, 6)), ref_time.year)
        month = get_first_not_none(
            (d.get('month{}'.format(i)) for i in range(1, 6)), ref_time.month)
        day = get_first_not_none(
            (d.get('day{}'.format(i)) for i in range(1, 6)), ref_time.day)
        year, month, day = int(year), int(month), int(day)
        if 1 <= month <= 12 and 1 <= day <= 31:
            result =  datetime.datetime(year, month, day)
            if (result - ref_time).days > 180:
                return None
            return result
        else:
            return None
    else:
        return None


def extract_time_from_content(text):
    m = re.search((
        r'活动日期[^年]*(?P<year1>\d{4})[^\d]*年[^\d]*(?P<month1>\d{1,2})[^\d]*月[^\d]*(?P<day1>\d{1,2})'
        r'|活动时间[^\d]*(?P<year2>\d{4})[^\d]*年[^\d]*(?P<month2>\d{1,2})[^\d]*月[^\d]*(?P<day2>\d{1,2})'
        r'|旅行时间[^\d]*(?P<year3>\d{4})[^\d]*年[^\d]*(?P<month3>\d{1,2})[^\d]*月[^\d]*(?P<day3>\d{1,2})'
        r'|活动日期[^d]*(?P<year4>\d{4})\.(?P<month4>\d{1,2})\.(?P<day4>\d{1,2})'
        r'|时间[^\d]*(?P<year5>\d{4})[^\d]*年[^\d]*(?P<month5>\d{1,2})[^\d]*月[^\d]*(?P<day5>\d{1,2})'
    ), text)
    if m:
        d = m.groupdict()
        year = d['year1'] or d['year2'] or d['year3'] or d['year4'] or d['year5']
        month = d['month1'] or d['month2'] or d['month3'] or d['month4'] or d['month5']
        day = d['day1'] or d['day2'] or d['day3'] or d['day4'] or d['day5']
        year, month, day = int(year), int(month), int(day)
        start_time = datetime.datetime(year=year, month=month, day=day)
        return start_time
    else:
        return None


def extract_money(html):
    text = HT.handle(html)
    m = re.search(
        r'每人(?P<money2>\d+).*元'
        r'|费用.*?(?P<money3>\d+).*?元'
        r'|活动费用.*?(?P<money4>\d+)RMB/人'
        r'|活动费用.*?(?P<money5>\d+)元'
        r'|每人(?P<money6>\d+)'
        r'(?P<money1>\d+).*?元/人',
        text,
        flags=re.DOTALL)
    if m:
        d = m.groupdict()
        money = get_first_not_none(
            (d.get('money{}'.format(i)) for i in range(1, 7)), None)
        return money
    else:
        return None


def get_activitys_by_page(page, pagesize=10, before=None, key=None):
    if page is None or page <= 0:
        page = 1
    if pagesize is None:
        pagesize = 10
    f = {'start_time': {'$gt': datetime.datetime.now()}}
    if before is not None and before:
        f['start_time']['$lt'] = datetime.datetime.now() \
                + datetime.timedelta(days=before+1)
    if key is not None and key:
        f['$or'] = [
            {
                'wechat_name': {
                    '$regex': key
                }
            },
            {
                'title': {
                    '$regex': key
                }
            },
        ]
    for i in outdoor_db.article.find(
            f,
            {
                '_id':0,
                'title':1,
                'created_at': 1,
                'start_time': 1,
                'wechat_name': 1,
                'fileid': 1,
                'money': 1,
            })\
            .sort([('start_time',1), ('_id', 1)])\
            .skip((page-1)*pagesize)\
            .limit(pagesize):
        i['created_at'] = i['created_at'].strftime('%Y-%m-%d')
        i['start_time'] = i['start_time'].strftime('%Y-%m-%d')
        yield i


def get_activity(fileid):
    fileid = int(fileid)
    return outdoor_db.article.find_one({'fileid': fileid})


def get_activity_outdoor_agg(before=None):
    """
    返回户外活动的总数量
    """
    f = {'start_time': {'$gt': datetime.datetime.now()}}
    if before is not None and before:
        f['start_time']['$lt'] = datetime.datetime.now() \
                + datetime.timedelta(days=before+1)

    for item in  outdoor_db.article.aggregate([
        {'$match': f},
        {'$group': {
            '_id': {
                'wechat_name': '$wechat_name'
            },
            'total': {
                '$sum': 1
            }
        }
    },
        {'$sort': SON([('total',-1)])}
        ]):
        _id = item.pop('_id')
        item.update(_id)
        yield item
