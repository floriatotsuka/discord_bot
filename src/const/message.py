class MainMessage:
    START_UP = "DISCORD BOT RUNNING..."


class VoicevoxBrokerMessage:
    DEBUG_MAKE_WAV_OK = "音声スピーチファイルを作成成功しました"


class DiscordBotHandlerMessage:
    COMMAND_TO_MESSAGE = {
        "/info": "私はあなたのテキストメッセージやファイルを、代わりに喋ったり歌ったりするBOTです。"
        "\nこのシステムは 'Discord.py, Google Cloud, VOICEVOX' の力を借りて構築されています。"
    }
    CONNECTION_OK = "接続しました。メッセージの読み上げなどのサポートを始めます。"
    CONNECTION_FAILED = "接続に失敗しました。時間をおいてやり直してください。"
    ALREADY_BOT_IN_SAME_VOICE_CHANNEL = "すでに同じボイスチャンネルにいます。"
    JOIN_REQUEST_FROM_ANOTHER_VOICE_CHANNEL = "別のボイスチャンネルでサポート中ですので開放されるまでお待ちください。"


class SystemMessage:
    SENDER_AND_BOT_IN_SAME_VOICE_CHANNEL = "BOTと同室のボイスチャンネルでのメッセージ発信"
    BOT_ARE_NOT_IN_SAME_VOICE_CHANNEL = "BOTの居ないボイスチャンネルでのメッセージ発信"
    ALREADY_BOT_IN_SAME_VOICE_CHANNEL = "同室のボイスチャンネルのテキストチャットから/joinされた"
    JOIN_REQUEST_FROM_ANOTHER_VOICE_CHANNEL = "別室のボイスチャンネルのテキストチャットから/joinされた"
