from discord_bot_handler import BotHandler
from voicevox.voicevox_broker import VoicevoxBroker
from dotenv import load_dotenv
import os
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG
from logging.handlers import TimedRotatingFileHandler
from const.config import LocalLoggerConfig, EnvironmentType
from const.message import MainMessage as MSG

load_dotenv()
ENV = os.environ["DISCORD_BOT_ENV"]
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
VOICEVOX_ENDPOINT = os.environ["VOICEVOX_ENDPOINT"]
LOGGING_PATH = os.environ["LOGGING_PATH"]

# 一元管理するロガーを生成
logger = getLogger(__name__)
st_handler = StreamHandler()
st_handler.setFormatter(Formatter(LocalLoggerConfig.FORMAT))
if ENV is EnvironmentType.PRODUCTION:
    st_handler.setLevel(INFO)
    tr_handler = TimedRotatingFileHandler(filename=LOGGING_PATH, encoding="utf-8")
    tr_handler.setFormatter(Formatter(format))
    tr_handler.setLevel(INFO)
    logger.addHandler(tr_handler)
    logger.setLevel(INFO)
else:
    st_handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
logger.addHandler(st_handler)
logger.propagate = False

# モジュールを生成
logger.info(MSG.START_UP)
vvb = VoicevoxBroker(VOICEVOX_ENDPOINT, logger)
bot = BotHandler(DISCORD_TOKEN, vvb, logger)
bot.run()
