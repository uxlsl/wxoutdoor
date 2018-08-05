import logging
import os

from dotenv import load_dotenv
import pymongo
import wechatsogou


load_dotenv(verbose=True)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='outdoor.log',
        level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=10)

client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
outdoor_db = client.outdoor
