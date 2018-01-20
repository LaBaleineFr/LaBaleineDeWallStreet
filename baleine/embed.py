""" Quick embed parser for loading files built by
    https://leovoel.github.io/embed-visualizer/
"""
from datetime import datetime
import discord
import yaml


class EmbedParsers(object):
    """ Simple collection of parsers for all embed elements """
    def __init__(self):
        raise NotImplementedError('Cannot be instantiated')

    parse_title = setattr
    parse_type = setattr
    parse_description = setattr
    parse_url = setattr
    parse_color = setattr
    parse_timestamp = setattr
    parse_image = setattr
    parse_thumbnail = setattr

    @staticmethod
    def parse_image(embed, key, value):
        embed.set_image(url=value)

    @staticmethod
    def parse_thumbnail(embed, key, value):
        embed.set_thumbnail(url=value)

    @staticmethod
    def parse_author(embed, key, value):
        embed.set_author(
            name=value.get('name', discord.Embed.Empty),
            url=value.get('url', discord.Embed.Empty),
            icon_url=value.get('icon_url', discord.Embed.Empty),
        )

    @staticmethod
    def parse_footer(embed, key, value):
        embed.set_footer(
            text=value.get('text', discord.Embed.Empty),
            icon_url=value.get('icon_url', discord.Embed.Empty),
        )

    @staticmethod
    def parse_fields(embed, key, value):
        for field in value:
            embed.add_field(
                name=field.get('name', discord.Embed.Empty),
                value=field.get('value', discord.Embed.Empty),
                inline=field.get('inline', True),
            )

def from_dict(data):
    embed = discord.Embed()

    for key, value in data.items():
        handler = getattr(EmbedParsers, 'parse_%s' % key, None)
        if handler:
            handler(embed, key, value)
    return embed

def from_yaml(stream):
    data = yaml.load(stream)
    return from_dict(data)
