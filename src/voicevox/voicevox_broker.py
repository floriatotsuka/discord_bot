import requests
import os

from const.config import VoicevoxBrokerConfig as CONFIG
from const.config import HTTP_STATUS
from const.message import VoicevoxBrokerMessage as MSG

from dataclasses import dataclass

# from lib.local_logger import LocalLogger

from logging import Logger


@dataclass
class VoicevoxBroker:
    """Voicevox server broker"""

    VOICEVOX_ENDPOINT: str
    logger: Logger

    SPEED_SCALE = CONFIG.SPEED_SCALE
    SAMPLING_RATE = CONFIG.SAMPLING_RATE
    SPEAKER = CONFIG.SPEAKER
    STATUS = HTTP_STATUS

    def get_speaker(self):
        return self.__get_speaker_list()

    def get_speech(self, message):
        mora = self.__retrieve_mora(message)
        return self.__retrieve_speech_signal(mora)

    def get_speech_file(self, message, *, filename="./test.wav"):
        """音声ファイルを作成してファイル名を返す"""
        wav = self.get_speech(message)
        filename = self.__create_audio_file(wav=wav, filename=filename)
        return filename

    def remove_speech_file(self, filename):
        os.remove(filename)
        self.logger.debug(filename)

    def __get_speaker_list(self):
        HEADER = {"accept": "application/json"}
        url = self.VOICEVOX_ENDPOINT + "/speakers"
        res = requests.get(url)
        return res.text

    def __retrieve_mora(self, message):
        """モーラの生成"""
        HEADER = {"accept": "application/json"}
        payload = {"text": message.content, "speaker": str(VoicevoxBroker.SPEAKER)}
        url = self.VOICEVOX_ENDPOINT + "/audio_query"
        res = requests.post(url, params=payload, headers=HEADER)
        mora = res.json()
        return mora

    def __retrieve_speech_signal(self, mora):
        """スピーチ音声の合成"""
        url = self.VOICEVOX_ENDPOINT + "/synthesis"
        HEADER = {"accept": "audio/wav", "Content-Type": "application/json"}
        payload = {
            "speaker": str(VoicevoxBroker.SPEAKER),
            "enable_interrogative_upspeak": "true",
        }
        mora["speedScale"] = VoicevoxBroker.SPEED_SCALE
        mora["outputSamplingRate"] = VoicevoxBroker.SAMPLING_RATE
        mora["outputStereo"] = False
        res = requests.post(url, params=payload, headers=HEADER, json=mora)

        wav = None
        if res.status_code == VoicevoxBroker.STATUS.OK:
            wav = res.content
        return wav

    def __create_audio_file(self, wav, filename):
        """音声ファイルをファイルに書き出し、そのファイル名を返す。"""
        with open(filename, "wb") as file:
            file.write(wav)
        self.logger.debug(MSG.DEBUG_MAKE_WAV_OK)
        return filename
