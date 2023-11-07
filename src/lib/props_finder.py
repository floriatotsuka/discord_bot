import discord


class PropsFinder:
    """(Discord)object propertie finder"""

    # コマンドに対応するリストデータを取得する関数を定義
    def get_info(message):
        command = message.content
        data_table = {
            "/members": message.guild.members,  # メンバーのリスト
            "/roles": message.guild.roles,  # 役職のリスト
            "/text_channels": message.guild.text_channels,  # テキストチャンネルのリスト
            "/voice_channels": message.guild.voice_channels,  # ボイスチャンネルのリスト
            "/category_channels": message.guild.categories,  # カテゴリチャンネルのリスト
        }
        return data_table.get(command, None)

    def is_voice_channel(message):
        """テキストメッセージが発せられたチャンネルがボイスチャンネル"""
        return message.channel.type is discord.ChannelType.voice

    def in_voice_channel(message):
        """テキストメッセージ発信者がボイスチャンネルのボイスチャットに参加しているか"""
        return message.author.voice is not None

    def is_bot_in_voice_channel(message):
        """BOTがの椅子チャンネルに参加済みか"""
        return message.guild.voice_client is not None
