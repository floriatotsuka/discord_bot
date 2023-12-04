from discord import ChannelType
from dataclasses import dataclass


@dataclass
class DiscordBroker:
    def is_message_from_participating_voice_channel(message) -> bool:
        """テキストメッセージ発信者がボイスチャンネルであるかを返す

        Args:
            message (discord.message): 入力メッセージ

        Returns:
            bool: ボイスチャンネルから発信されたかメッセージか
        """

    def is_bot_message(message) -> bool:
        """BOTから発せられたメッセージであるかを返す

        Args:
            message (discord.message): 入力メッセージ

        Returns:
            bool: BOTから発信されたかメッセージか
        """
        return message.author.bot

    def is_send_on_voice_channel(message) -> bool:
        """テキストメッセージが発せられたチャンネルがボイスチャンネルであるかを返す

        Args:
            message (discord.message): 入力メッセージ

        Returns:
            bool: ボイスチャンネルから発信されたかメッセージか
        """
        return message.channel.type is ChannelType.voice

    def is_send_on_text_channel(message) -> bool:
        """テキストメッセージが発せられたチャンネルがテキストチャンネルであるかを返す

        Args:
            message (discord.message): 入力メッセージ

        Returns:
            bool: テキストチャンネルから発信されたかメッセージか
        """
        return message.channel.type is ChannelType.text

    def is_participate_in_voice_channel(author) -> bool:
        """テキストメッセージ発信者がボイスチャンネルのボイスチャットに参加中か

        Args:
            message (discord.message.author): 入力メッセージ発信者

        Returns:
            bool: メッセージ発信者がボイスチャンネルに参加中ならばTrue
        """
        return author.voice is not None

    def is_bot_joining_voice_channel(message):
        """BOTがボイスチャットに参加中か

        Args:
            message (discord.message): 入力メッセージ発信者

        Returns:
            bool: メッセージ発信者のギルドでBOTがすでにボイスチャンネル参加中ならTrue
        """
        return message.guild.voice_client is not None

    def is_sender_and_bot_in_same_voice_channel(message):
        """メッセージ発信者とBOTが同じボイスチャットに参加中かつ
            そのボイスチャンネルで発信されたメッセージであるか

        Args:
            message (discord.message): 入力メッセージ発信者

        Returns:
            bool: メッセージ発信者とBOTとテキストメッセージが発信されたボイスチャンネルが同一ならTrue
        """
        bot_voice_client = message.guild.voice_client
        sender_voice_client = message.author.voice

        if bot_voice_client is None:
            # メッセージが発信されたギルドのボイスチャンネルにBOTが参加していない
            return False

        return sender_voice_client.channel.id is bot_voice_client.channel.id
