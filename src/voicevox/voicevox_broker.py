import requests

class VoicevoxBroker:
    """ Voicevox server broker """

    SPEED_SCALE = 1.3
    SAMPLING_RATE = 16000
    SPEAKER = 1 # is ずんだもん

    def __init__(self, endpoint, logger):
        self.VOICEVOX_ENDPOINT = endpoint
        self.logger = logger
        logger.debug("setup VoicevoxBroker")
    
    def get_speach(self, message):

        mora = self.__make_mora(message)
        return self.__speech_synthesis(mora)

    def __make_mora(self, message):
        """ モーラの生成 """
        HEADER = {'accept': 'application/json'}
        payload={
            'text' : message.content,
            'speaker' : str(VoicevoxBroker.SPEAKER)
        }
        url = self.VOICEVOX_ENDPOINT + '/audio_query'
        res_mora = requests.post(url, params=payload, headers=HEADER)

        mora = res_mora.json()
        mora['speedScale'] = VoicevoxBroker.SPEED_SCALE
        mora['outputSamplingRate'] = VoicevoxBroker.SAMPLING_RATE
        mora['outputStereo'] = False
        return mora

    def __speech_synthesis(self, mora):
        """ スピーチ音声の合成 """
        url = self.VOICEVOX_ENDPOINT + '/synthesis'
        HEADER = {
            'accept': 'audio/wav',
            'Content-Type': 'application/json'
        }
        payload={
            'speaker' : str(VoicevoxBroker.SPEAKER),
            'enable_interrogative_upspeak' : 'true'
        }
        res = requests.post(url, params=payload, headers=HEADER, json=mora)

        audio = None
        if res.status_code == 200: # HTTP Status 200 OK
            audio = res.content
            with open('./test.wav', "wb") as file: #FIXME:
                file.write(audio)
            self.logger.debug("✅ audio file downloaded successfully.")
        return audio
