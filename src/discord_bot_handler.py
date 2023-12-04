import discord
from discord import ChannelType
import os

from const.config import DiscordBotConfig as CONFIG
import const.command as COMMAND
from const.message import DiscordBotHandlerMessage as MSG
from const.message import SystemMessage as SYS

from dataclasses import dataclass
from collections import defaultdict, deque
import asyncio

from voicevox.voicevox_broker import VoicevoxBroker
from discord_broker import DiscordBroker
from logging import Logger


@dataclass
class BotHandler:
    token: str
    vss: VoicevoxBroker
    logger: Logger

    all_queue_dict = defaultdict(deque)
    audio_file_dict = defaultdict(deque)

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
            """Discordのメッセージが発生した時の処理

            Args:
                message (discord.Message): 入力メッセージ
            """
            self.logger.info(
                f'Message from {message.author}: "{message.content}" {message.channel}({message.channel.id})'
            )

            # Botが発信したテキストメッセージを無視する
            if self.__is_bot_message(message):
                return

            match message.channel.type:
                case ChannelType.text:
                    await self.__text_channel_handler(message)
                case ChannelType.voice:
                    await self.__voice_channel_handler(message)
                case _:
                    self.logger.info(
                        "Out-of-scope ChannelType :" + message.channel.type
                    )

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

    def __is_bot_message(self, message):
        """メッセージ発信元がBOTであるか(ラッパー)"""
        return DiscordBroker.is_bot_message(message)

    async def __text_channel_handler(self, message):
        """テキストチャンネル中でのやり取りハンドラ"""
        if message.content in MSG.COMMAND_TO_MESSAGE.keys():
            # コマンドを受信した場合の処理
            await self.__command_control_on_text_channel(message)

    async def __voice_channel_handler(self, message):
        """ボイスチャンネルのメッセージに合わせてBOT操作かテキストを代弁する"""
        if message.content in COMMAND.FOR_TEXT_CHAT:
            # コマンドを受信した場合の処理
            await self.__command_control_on_voice_channel(message=message)
        else:
            # コマンド外のメッセージを受信した場合の処理
            if DiscordBroker.is_sender_and_bot_in_same_voice_channel(message):
                await self.__text_to_speech(message)
                self.logger.debug(SYS.SENDER_AND_BOT_IN_SAME_VOICE_CHANNEL)
            else:
                self.logger.debug(SYS.BOT_ARE_NOT_IN_SAME_VOICE_CHANNEL)

    async def __command_control_on_voice_channel(self, message):
        """ボイスチャンネル中で有効な独自コマンドを処理する"""
        match message.content:
            case COMMAND.CONNECT:
                if DiscordBroker.is_bot_joining_voice_channel(message) is False:
                    self.logger.debug(
                        "BOTがボイスチャンネルに参加していないがボイスチャンネルのテキストチャットから/joinされた"
                    )
                    try:
                        await self.__join_voice_channel(message)
                        _ = self.vss.get_speaker()  # pre-warming for Cloud Run
                    except discord.errors.ClientException:
                        await message.channel.send(MSG.CONNECTION_FAILED)
                elif DiscordBroker.is_sender_and_bot_in_same_voice_channel(message):
                    await message.channel.send(MSG.ALREADY_BOT_IN_SAME_VOICE_CHANNEL)
                    self.logger.debug(SYS.ALREADY_BOT_IN_SAME_VOICE_CHANNEL)
                else:
                    await message.channel.send(
                        MSG.JOIN_REQUEST_FROM_ANOTHER_VOICE_CHANNEL
                    )
                    self.logger.debug(SYS.JOIN_REQUEST_FROM_ANOTHER_VOICE_CHANNEL)

            case COMMAND.DISCONNECT:
                if DiscordBroker.is_bot_joining_voice_channel(message) is False:
                    await message.channel.send("もともとボイスチャンネルに参加していませんよ")
                    self.logger.debug("BOTがボイスチャンネルに参加していないがボイスチャンネルのテキストチャットから/byeされた")
                elif DiscordBroker.is_sender_and_bot_in_same_voice_channel(message):
                    await message.guild.voice_client.disconnect()
                    self.logger.debug("同室のボイスチャンネルのテキストチャットから/byeされた")
                else:
                    self.logger.debug("別室のボイスチャンネルのテキストチャットから/byeされた")
            case _:
                self.logger.warn("Unknown command: " + message.content)

    async def __join_voice_channel(self, message):
        await message.author.voice.channel.connect()
        await message.channel.send(MSG.CONNECTION_OK)

    async def __command_control_on_text_channel(self, message):
        command = message.content
        msg = MSG.COMMAND_TO_MESSAGE.get(command, None)
        if msg != None:
            await message.channel.send(msg)

    async def __text_to_speech(self, message):
        guild_queue = self.all_queue_dict[message.guild.id]
        file_queue = self.audio_file_dict[message.guild.id]
        fn = CONFIG.SPEECH_FILE_ROOT + str(message.id) + ".wav"

        # 音声ファイル作成する(ライブラリ内でffmpegを利用しているためファイル化する必要があるため)
        try:
            _ = self.vss.get_speech_file(message, filename=fn)
            guild_queue.append(
                {
                    "audio": discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(fn)),
                    "file": fn,
                }
            )
            self.logger.debug("Make speech file: " + fn)
        except:
            self.logger.error("File operation failed: " + fn)
        finally:
            self.logger.info("voice file created: " + fn)

        # 音声ファイル再生と再生後の削除
        try:
            _ = self.__speech(message.guild.voice_client, guild_queue, file_queue)
        except:
            self.logger.error("Speech operation failed: " + fn)
        finally:
            self.logger.info("Speech operation completed: " + fn)

    def __speech(self, voice_client, queue, files):
        """音声再生する
        voice_client: ギルドに応じた音声クライアント
        queue: ギルド毎のキュー(中身はdiscord.AudioSourceと元ファイル名)
        files: スピーチ済みのファイルリスト
        任意のギルドの音声キューと対応するデータ削除用filesのセットでコールされる"""
        if voice_client.is_playing():
            # スピーチ中に付き保留
            return False
        if not queue and not files:
            # 通常終了
            return True
        if not queue and files:
            # ファイルを消す
            self.__delete_audio_files(files)
            return False

        source = queue.popleft()
        files.append(source["file"])
        voice_client.play(
            source["audio"], after=lambda e: self.__speech(voice_client, queue, files)
        )
        return False

    def __delete_audio_files(self, queue):
        while queue:
            self.logger.debug(queue)
            os.remove(queue.popleft())
        return True
