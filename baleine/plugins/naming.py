import baleine.bot
import discord
import logging
import random
import re

logger = logging.getLogger(__name__)

class Naming(object):
    """ Simple plugin that renames users violating the naming policy """

    must_match = None
    badwords = None

    messages = {
        'badname': 'Le nom que vous avez choisi n\'est pas autorisé sur ce serveur. '
                   'En attendant que vous le changiez, je vous en ai choisi un.',
    }

    nicknames = [
        'Alex', 'Ange', 'Camille', 'Charlie', 'Claude', 'Dany', 'Fred', 'Hippolyte',
        'Jackie', 'Leslie', 'Lou', 'Maxime', 'Morgan', 'Sacha', 'Stéphane', 'Yannick',
    ]

    translation = str.maketrans(
        '0135@!ÀÂÄÇÉÈÊËÎÏÛÜÔÖaàâäbcçdeéèêëfghiîïjklmnoôöpqrstuùûüvwxyz',
        'OIESAIAAACEEEEIIUUOOaaaabccdeeeeefghiiijkimnooopqrstuuuuvwxyz',
        '+=<>~-_.,: '
    )


    def __init__(self, config):
        try:
            self.channel = config['channel']
        except KeyError:
            raise baleine.bot.ConfigError('Naming plugin requires a channel')

        must_match = config.get('must_match')
        if must_match:
            self.must_match = re.compile(must_match, re.IGNORECASE)

        badwords = config.get('badwords')
        if badwords:
            with open(badwords, 'r') as fd:
                self.badwords = [line.strip().translate(self.translation).lower()
                                 for line in fd if line.strip()]

    async def on_member_join(self, client, member):
        if not member.bot and not self.check(member.nick or member.name):
            await self.act(client, member)

    async def on_member_update(self, client, before, after):
        if not after.bot and not self.check(after.nick or after.name):
            await self.act(client, after)

    def check(self, name):
        if self.must_match and not self.must_match.fullmatch(name):
            return False

        simplified = name.translate(self.translation).lower()
        if any(word in simplified for word in self.badwords):
            return False
        return True

    async def act(self, client, member):
        old = member.nick or member.name
        nickname = await self.pick_nickname(client, member)

        try:
            await client.change_nickname(member, nickname)
        except discord.errors.Forbidden:
            logger.info('not renaming {user} [{userid}]: forbidden'.format(
                        user=member.name, userid=member.id))
            return
        else:
            logger.info('renamed {user} [{userid}] from {old} to {new}'.format(
                        user=member.name, userid=member.id,
                        old=old,
                        new=nickname))

        message = self.messages['badname'].format(name=member.name)
        try:
            await client.send_message(member, message)
        except discord.errors.Forbidden:
            await client.send_message(self.channel, '%s: %s' % (member.mention, message))

    async def pick_nickname(self, client, member):
        return random.choice(self.nicknames)
