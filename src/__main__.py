from discord_bot_handler import BotHandler
from voicevox.voicevox_broker import VoicevoxBroker
from lib.local_logger import LocalLogger
from dotenv import load_dotenv
import os
import logging

load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
VOICEVOX_ENDPOINT = os.environ["VOICEVOX_ENDPOINT"]

logger = LocalLogger(level=logging.INFO)
logger.info("RUN DISCORD BOT!!!")
vvb = VoicevoxBroker(VOICEVOX_ENDPOINT, logger=logger)
bot = BotHandler(discord_token=DISCORD_TOKEN, voice_speech_synthesis=vvb, logger=logger)
bot.run()
