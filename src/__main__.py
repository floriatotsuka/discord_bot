from discord_bot_handler import BotHandler
from voicevox.voicevox_broker import VoicevoxBroker
from lib.local_logger import LocalLogger
from dotenv import load_dotenv
import os
import logging
from const.message import MainMessage as MSG

load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
VOICEVOX_ENDPOINT = os.environ["VOICEVOX_ENDPOINT"]

logger = LocalLogger(level=logging.INFO)
logger.info(MSG.START_UP)
vvb = VoicevoxBroker(VOICEVOX_ENDPOINT, logger)
bot = BotHandler(DISCORD_TOKEN, vvb, logger)
bot.run()
