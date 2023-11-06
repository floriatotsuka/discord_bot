import discord
from lib.props_finder import PropsFinder as prop
import const.command as COMMAND
import const.message as MSG
# import asyncio

class BotHandler:

    def __init__(self, discord_token, voice_speech_synthesis, logger):
        self.token = discord_token
        self.vss = voice_speech_synthesis
        self.logger = logger
        self.logger.debug("init BotHandler")

    def run(self):
        """ Listen状態のサーバのリスナ定義 """

        # 接続オブジェクトを生成
        client = discord.Client(intents = discord.Intents.all())

        # 起動時の処理
        @client.event
        async def on_ready():
            self.logger.info(f'Login "{client.guilds[0]}"(id:{client.guilds[0].id}, owner: {client.application.owner}, latency: {round(client.latency, 3)}) by {client.application.name}')

        # メッセージ受信時の処理
        @client.event
        async def on_message(message):
            self.logger.info(f'Message from {message.author}: "{message.content}" {message.channel}({message.channel.id})')

            if message.author.bot:
                # メッセージ送信者がBotならば無視
                return

            if prop.is_voice_channel(message=message) and prop.in_voice_channel(message=message):
                # ボイスチャンネル向けの返答
                await self.__reaction_speach_for_voice_ch(message=message)
            else:
                # テキストチャンネル向けの返答
                await self.__reaction_message_for_txet_ch(message=message)

        # Discordサーバーへ接続
        client.run(self.token)
    
    async def __reaction_message_for_txet_ch(self, message):
        """ 特定のキーワードに向けて情報を返す """
        msg = prop.get_info(message=message)
        if msg != None:
            await message.channel.send(msg)
    
    async def __reaction_speach_for_voice_ch(self, message):
        """ ボイスチャンネルにスピーチ音声を返す """
        if message.content in COMMAND.LIST:
            await self.__command_control_on_voice_channel(message=message)
        else:
            if prop.is_bot_in_voice_channel(message=message): # TODO:　かつ該当チャンネルにいるのか
                try:
                    fn = './temp/' + str(message.id) + '.wav'
                    filename = self.vss.get_speach_file(message=message, filename=fn)
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename))
                    message.guild.voice_client.play(source)
                finally:
                    print("Clean up")
                    # self.vss.cleanup_speach_file(filename) TODO: play後に削除
                self.logger.debug("speach reaction: OK")

    async def __command_control_on_voice_channel(self, message):
        """ ボイスチャンネル中で有効な独自コマンドを処理する """
        match message.content:
            case COMMAND.CONNECT:
                if prop.is_bot_in_voice_channel(message=message):
                    # TODO:　かつ該当チャンネルにはいない
                    print("チャンネルを移動")
                    # TODO: 該当チャンネルにすでにいる
                    return
                else:
                    # ボイスチャンネルに接続する
                    try:
                        await message.author.voice.channel.connect()
                        await message.channel.send(MSG.CONNECTION_OK)
                    except discord.errors.ClientException:
                        await message.channel.send(MSG.CONNECTION_FAILED)
            case COMMAND.DISCONNECT:
                if prop.is_bot_in_voice_channel(message=message): # TODO:　かつ該当チャンネルにいるのか
                    # ボイスチャンネルを切断する
                    await message.guild.voice_client.disconnect()
            # その他
            case _:
                self.logger.warn("Unknown command")
