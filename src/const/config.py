class VoicevoxBrokerConfig:
    SPEED_SCALE = 1.3
    SAMPLING_RATE = 16000
    SPEAKER = 1  # is ずんだもん


class DiscordBotConfig:
    SPEECH_FILE_ROOT = "./temp/"
    TIME_LIMIT_OF_WAITING = 180
    SPEECH_ALLOWED_TIME = 60


class LocalLoggerConfig:
    FORMAT = "%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"


class EnvironmentType:
    PRODUCTION = "production"


class HTTP_STATUS:
    OK = 200
