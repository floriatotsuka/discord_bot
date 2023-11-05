import discord
from lib.props_finder import PropsFinder as prop

class BotHandler:

    def __init__(self, discord_token, voice_speech_synthesis, logger):
        self.token = discord_token
        self.vss = voice_speech_synthesis
        self.logger = logger
        logger.debug("setup BotHandler")

    def run(self):        
        # 接続オブジェクトを生成
        client = discord.Client(intents = discord.Intents.all())

        # 起動時の処理
        @client.event
        async def on_ready():
            self.__ready(client=client)

        # メッセージ受信時の処理
        @client.event
        async def on_message(message):
            self.__talk_logging(message=message)

            if message.author.bot:
            # メッセージ送信者がBotならば無視
                return

            if prop.is_voice_channel(message):
                audio = self.vss.get_speach(message=message)
                if audio != None:
                    await self.__reaction_speach_for_voice_ch(message=message, audio=audio)
            else:
                await self.__reaction_message_for_txet_ch(message=message)

        # Discordサーバーへ接続
        client.run(self.token)
    
    def __ready(self, client):
        """ Discordサーバへログインのロギング """
        self.logger.info(f'Login "{client.guilds[0]}"(id:{client.guilds[0].id}, owner: {client.application.owner}, latency: {round(client.latency, 3)}) by {client.application.name}')
    
    def __talk_logging(self, message):
        """ テキストメッセージのロギング """
        self.logger.info(f'Message from {message.author}: "{message.content}" {message.channel}({message.channel.id})')
    
    async def __reaction_message_for_txet_ch(self, message):
        """ 特定のキーワードに向けて情報を返す """
        msg = prop.get_info(message=message)
        if msg != None:
            await message.channel.send(msg)
    
    async def __reaction_speach_for_voice_ch(self, message, audio):
        """ ボイスチャンネルにスピーチ音声を返す TODO: """
        # try:
        #     await message.channel.send("test @ try")
        #     vc = await message.channel.connect()
        #     vc.play(discord.FFmpegPCMAudio("./test.wav"))
        #     while vc.is_playing():
        #         await asyncio.sleep(1)
        # finally:
        #     await message.channel.send("test @ final")
        #     await vc.disconnect(message.channel)
