import re
import datetime


def get_first_not_none(lst, v=None):
    return next(
            (item for item in lst if item is not None),
            v)

def extract_time_from_title(text):
    """
    提取第一个时间
    """
    now = datetime.datetime.now()
    m = re.search((
        r'(?P<month1>\d{1,2})月(?P<day1>\d{1,2})'
        r'|(?P<year2>\d{4})\.(?P<month2>\d{1,2})\.(?P<day2>\d{1,2})'
        r'|(?P<year3>\d{4})年【(?P<month3>\d{1,2})\.(?P<day3>\d{1,2})'
        r'|(?P<year4>\d{4})年(?P<month4>\d{1,2})月(?P<day4>\d{1,2})'
        r'|(?P<month5>\d{1,2})\.(?P<day5>\d{1,2})'
        ), text)
    if m:
        d = m.groupdict()
        year = get_first_not_none(
                (d.get('year{}'.format(i)) for i in range(1, 6)),
                now.year)
        month = get_first_not_none(
                (d.get('month{}'.format(i)) for i in range(1, 6)),
                now.month)
        day  = get_first_not_none(
                (d.get('day{}'.format(i)) for i in range(1, 6)),
                now.day)
        year, month, day = int(year), int(month),int(day)
        if 1<=month<=12 and 1<=day<=31:
            return datetime.datetime(year,month, day)
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
        year, month, day = int(year),int(month), int(day)
        start_time = datetime.datetime(year=year, month=month, day=day)
        return start_time
    else:
        return None
