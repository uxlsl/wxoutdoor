from datetime import datetime
from utils import extract_time_from_title


def test_extract_time_from_title():
    assert extract_time_from_title('6月23日') == datetime(2018,6,23)
    assert extract_time_from_title('2018.8.19-8.25') == datetime(2018,8,19)
    assert extract_time_from_title('2018年【8.20-8.26】') == datetime(2018,8,20)
    assert extract_time_from_title('2018年8月4-9日') == datetime(2018,8,4)
    assert extract_time_from_title('5月26-27日') == datetime(2018,5,26)
