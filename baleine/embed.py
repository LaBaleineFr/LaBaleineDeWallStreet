""" Quick embed parser for loading files built by
    https://leovoel.github.io/embed-visualizer/
"""
from datetime import datetime
import discord
import yaml
from baleine import emoji


class Parser(object):
    """ Simple collection of parsers for all embed elements """
    def __init__(self, guild=None):
        self.guild = guild
        self.emoji_dict = None if guild is None else emoji.build_emoji_dict(guild)

    def from_dict(self, data):
        embed = discord.Embed()

        for key, value in data.items():
            handler = getattr(self, 'parse_%s' % key, None)
            if handler:
                handler(embed, key, value)
        return embed

    def from_yaml(self, stream):
        data = yaml.load(stream)
        return self.from_dict(data)

    def handle_emojis(self, text):
        if text is discord.Embed.Empty:
            return text
        return emoji.parse_emojis(text, custom=self.emoji_dict)

    def passthrough(self, embed, key, value):
        setattr(embed, key, self.handle_emojis(value))

    parse_title = passthrough
    parse_type = setattr
    parse_description = passthrough
    parse_url = setattr
    parse_color = setattr
    parse_timestamp = setattr
    parse_image = setattr
    parse_thumbnail = setattr

    def parse_image(self, embed, key, value):
        embed.set_image(url=value)

    def parse_thumbnail(self, embed, key, value):
        embed.set_thumbnail(url=value)

    def parse_author(self, embed, key, value):
        embed.set_author(
            name=self.handle_emojis(value.get('name', discord.Embed.Empty)),
            url=value.get('url', discord.Embed.Empty),
            icon_url=value.get('icon_url', discord.Embed.Empty),
        )

    def parse_footer(self, embed, key, value):
        embed.set_footer(
            text=self.handle_emojis(value.get('text', discord.Embed.Empty)),
            icon_url=value.get('icon_url', discord.Embed.Empty),
        )

    def parse_fields(self, embed, key, value):
        for field in value:
            embed.add_field(
                name=self.handle_emojis(field.get('name', discord.Embed.Empty)),
                value=self.handle_emojis(field.get('value', discord.Embed.Empty)),
                inline=field.get('inline', True),
            )
