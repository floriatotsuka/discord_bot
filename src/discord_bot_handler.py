import discord
from lib.props_finder import PropsFinder as prop
import const.command as COMMAND
import const.message as MSG

from dataclasses import dataclass
import asyncio

from voicevox.voicevox_broker import VoicevoxBroker
from lib.local_logger import LocalLogger


@dataclass
class BotHandler:
    token: str
    vss: VoicevoxBroker
    logger: LocalLogger

    def run(self):
        """Listen状態のサーバのリスナ定義"""

        # 接続オブジェクトを生成
        client = discord.Client(intents=discord.Intents.all())

        # 起動時の処理
        @client.event
        async def on_ready():
            self.logger.info(
                f'Login "{client.guilds[0]}"(id:{client.guilds[0].id}, owner: {client.application.owner}, latency: {round(client.latency, 3)}) by {client.application.name}'
            )

        # メッセージ受信時の処理
        @client.event
        async def on_message(message):
            self.logger.info(
                f'Message from {message.author}: "{message.content}" {message.channel}({message.channel.id})'
            )
            # メッセージ送信者がBotならば無視
            if message.author.bot:
                return

            if self.__is_message_by_voice_channel_participant(message=message):
                # ボイスチャンネルからのメッセージ向けのアクション
                await self.__reaction_speach_for_voice_ch(message=message)
            elif self.__is_message_from_voice_channel(message=message) is False:
                # テキストチャンネルからのメッセージ向けのアクション
                await self.__reaction_message_for_txet_ch(message=message)
            else:
                self.logger.debug("ボイスチャンネルのボイスチャットに参加していないユーザのテキストメッセージ")

        # チャンネル入退場時の処理
        @client.event
        async def on_voice_state_update(member, before, after):
            if before.channel != after.channel:
                # 退室通知
                if before.channel is not None:
                    self.logger.debug(
                        before.channel.name + " から、" + member.name + " が退場しました。"
                    )
                # 入室通知
                if after.channel is not None:
                    self.logger.debug(
                        after.channel.name + " に、" + member.name + " が参加しました。"
                    )

            voice_state = member.guild.voice_client
            if voice_state is not None:
                if len(voice_state.channel.members) == 1:
                    await voice_state.disconnect()

        # Discordサーバーへ接続
        client.run(self.token)

    async def __reaction_message_for_txet_ch(self, message):
        """任意のコマンドに向けて情報を返す"""
        msg = prop.get_info(message=message)
        if msg != None:
            await message.channel.send(msg)

    async def __reaction_speach_for_voice_ch(self, message):
        """ボイスチャンネルのメッセージに合わせてBOT操作かテキストを代弁する"""
        if message.content in COMMAND.LIST:
            await self.__command_control_on_voice_channel(message=message)
        else:
            if self.__is_bot_joining_voice_channel(
                message=message
            ) and self.__is_sender_and_bot_in_same_voice_channel(message=message):
                try:
                    fn = "./temp/" + str(message.id) + ".wav"
                    filename = self.vss.get_speach_file(message=message, filename=fn)
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(filename)
                    )

                    message.guild.voice_client.play(source)
                    timeout = 20
                    while message.guild.voice_client.is_playing():
                        if timeout > 0:
                            timeout -= 1
                            await asyncio.sleep(1)
                        else:
                            break
                finally:
                    self.vss.remove_speach_file(filename)
                self.logger.debug("BOTと同室のボイスチャンネルでのテキストメッセージ")
            else:
                self.logger.debug("BOTとは別室のボイスチャンネルでのテキストメッセージ")

    async def __command_control_on_voice_channel(self, message):
        """ボイスチャンネル中で有効な独自コマンドを処理する"""
        match message.content:
            case COMMAND.CONNECT:
                if self.__is_bot_joining_voice_channel(message=message) is False:
                    self.logger.debug(
                        "BOTがボイスチャンネルに参加していないがボイスチャンネルのテキストチャットから/joinされた"
                    )
                    try:
                        await message.author.voice.channel.connect()
                        await message.channel.send(MSG.CONNECTION_OK)
                    except discord.errors.ClientException:
                        await message.channel.send(MSG.CONNECTION_FAILED)
                elif self.__is_sender_and_bot_in_same_voice_channel(message=message):
                    self.logger.debug("同室のボイスチャンネルのテキストチャットから/joinされた")
                    await message.channel.send("すでに同じボイスチャンネルに居ますよ")
                else:
                    self.logger.debug("別室のボイスチャンネルのテキストチャットから/joinされた")
                    await message.channel.send("別のボイスチャンネルでサポート中ですので開放されるまでお待ちください。")

            case COMMAND.DISCONNECT:
                if self.__is_bot_joining_voice_channel(message=message) is False:
                    self.logger.debug("BOTがボイスチャンネルに参加していないがボイスチャンネルのテキストチャットから/byeされた")
                    await message.channel.send("もともとボイスチャンネルに参加していませんよ")
                elif self.__is_sender_and_bot_in_same_voice_channel(message=message):
                    self.logger.debug("同室のボイスチャンネルのテキストチャットから/byeされた")
                    await message.guild.voice_client.disconnect()
                else:
                    self.logger.debug("別室のボイスチャンネルのテキストチャットから/byeされた")
            case _:
                self.logger.warn("Unknown command")

    def __is_message_from_voice_channel(self, message):
        """テキストメッセージが発せられたチャンネルがボイスチャンネルか"""
        return message.channel.type is discord.ChannelType.voice

    def __is_sender_in_voice_channel(self, message):
        """テキストメッセージ発信者がボイスチャンネルのボイスチャットに参加しているか"""
        return message.author.voice is not None

    def __is_sender_and_bot_in_same_voice_channel(self, message):
        """テキストメッセージ発信者とBOTが同じボイスチャンネルに居るか"""
        sender_ch = message.author.voice.channel.id
        bot_ch = message.guild.voice_client.channel.id
        return sender_ch is bot_ch

    def __is_message_by_voice_channel_participant(self, message):
        """テキストメッセージ発信者がボイスチャットに参加しており、そのテキストチャットからメッセージ発信したか"""
        return self.__is_message_from_voice_channel(
            message=message
        ) and self.__is_sender_in_voice_channel(message=message)

    def __is_bot_joining_voice_channel(self, message):
        """BOTがボイスチャットに参加しているか"""
        return message.guild.voice_client is not None
