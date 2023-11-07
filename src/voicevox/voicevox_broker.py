import requests
import os
import random


class VoicevoxBroker:
    """Voicevox server broker"""

    SPEED_SCALE = 1.3
    SAMPLING_RATE = 16000
    SPEAKER = 1  # is ずんだもん

    def __init__(self, endpoint, logger):
        self.VOICEVOX_ENDPOINT = endpoint
        self.logger = logger
        logger.debug("setup VoicevoxBroker")

    def get_speach(self, message):
        mora = self.__make_mora(message)
        return self.__speech_synthesis(mora)

    def get_speach_file(self, message, *, filename="./test.wav"):
        """音声ファイルを作成してファイル名を返す"""
        wav = self.get_speach(message)
        filename = self.__make_audio_file(wav=wav, filename=filename)
        return filename

    def cleanup_speach_file(self, filename):
        # TODO:
        os.remove(filename)
        self.logger.debug(filename)

    def __make_mora(self, message):
        """モーラの生成"""
        HEADER = {"accept": "application/json"}
        payload = {"text": message.content, "speaker": str(VoicevoxBroker.SPEAKER)}
        url = self.VOICEVOX_ENDPOINT + "/audio_query"
        res = requests.post(url, params=payload, headers=HEADER)

        mora = res.json()
        mora["speedScale"] = VoicevoxBroker.SPEED_SCALE
        mora["outputSamplingRate"] = VoicevoxBroker.SAMPLING_RATE
        mora["outputStereo"] = False
        return mora

    def __speech_synthesis(self, mora):
        """スピーチ音声の合成"""
        url = self.VOICEVOX_ENDPOINT + "/synthesis"
        HEADER = {"accept": "audio/wav", "Content-Type": "application/json"}
        payload = {
            "speaker": str(VoicevoxBroker.SPEAKER),
            "enable_interrogative_upspeak": "true",
        }
        res = requests.post(url, params=payload, headers=HEADER, json=mora)

        wav = None
        if res.status_code == 200:  # HTTP Status 200 OK
            wav = res.content
        return wav

    def __make_audio_file(self, wav, filename):
        """音声ファイルをファイルに書き出し、そのファイル名を返す。"""
        with open(filename, "wb") as file:
            file.write(wav)
        self.logger.debug("audio file downloaded successfully.")
        return filename
