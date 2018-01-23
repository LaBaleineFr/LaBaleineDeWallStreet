import baleine.bot
from collections import namedtuple
import discord
import logging
import random
import re
from baleine import util

logger = logging.getLogger(__name__)

class Naming(object):
    """ Simple plugin that renames users violating the naming policy """

    Filter = namedtuple('Filter', 'match message')

    filters = None
    badwords = None

    messages = {
        'badword': 'Votre nom contient la séquence interdite « {word} ». '
                   'Je vous ai renommé, vous pouvez choisir un autre pseudo d\'un clic droit sur '
                   'votre nom dans le chat.',
    }

    nicknames = [
        'Alex', 'Ange', 'Camille', 'Charlie', 'Claude', 'Dany', 'Fred', 'Hippolyte',
        'Jackie', 'Leslie', 'Lou', 'Maxime', 'Morgan', 'Sacha', 'Stéphane', 'Yannick',
    ]

    translation = str.maketrans(
        '0135$@!ÀÂÄÇÉÈÊËÎÏÛÜÔÖaàâäbcçdeéèêëfghiîïjklmnoôöpqrstuùûüvwxyz',
        'OIESSAIAAACEEEEIIUUOOaaaabccdeeeeefghiiijkimnooopqrstuuuuvwxyz',
        '&()[]{}<>|_^=+,.:/\;*? '
    )


    def __init__(self, config):
        try:
            self.channel = config['channel']
        except KeyError:
            raise baleine.bot.ConfigError('Naming plugin requires a channel')

        self.filters = [
            self.Filter(re.compile(item['match'], re.IGNORECASE), item['message'])
            for item in config.get('filters', [])
        ]

        badwords = config.get('badwords')
        if badwords:
            with open(badwords, 'r') as fd:
                self.badwords = [line.strip().translate(self.translation).lower()
                                 for line in fd if line.strip()]

    # Event handlers
    async def on_member_join(self, client, member):
        if member.top_role < member.server.me.top_role and not member.bot:
            await self.check_name(client, member)

    async def on_member_update(self, client, before, after):
        if after.top_role < after.server.me.top_role and not after.bot:
            await self.check_name(client, after)

    # Actual work
    async def check_name(self, client, member):
        # If name is valid, don't do anything
        name = member.nick or member.name
        valid, reason = self.check(name)
        if valid:
            return

        # Name not valid, see whether we can make it valid by dropping unicode features
        suggestion = util.simplify_unicode(name)
        valid, reason = self.check(suggestion)
        if valid:
            # yes, then rename with no warning
            await self.rename(client, member, suggestion)
            return

        # No, name really is invalid, pick a new one and warn
        suggestion = await self.pick_nickname(client, member)
        await self.rename(client, member, suggestion, reason)

    def check(self, name):
        for item in self.filters:
            if not item.match.fullmatch(name):
                return False, item.message

        simplified = util.simplify_unicode(name).translate(self.translation).lower()
        for word in self.badwords:
            if word in simplified:
                return False, self.messages['badword'].format(word=word)
        return True, None

    async def pick_nickname(self, client, member):
        return random.choice(self.nicknames)

    async def rename(self, client, member, name, reason=None):
        old = member.nick or member.name

        try:
            await client.change_nickname(member, name)
        except discord.errors.Forbidden:
            logger.info('not renaming {user} [{userid}]: forbidden'.format(
                        user=member.name, userid=member.id))
            return
        else:
            logger.info('renamed {user} [{userid}] from {old} to {new}'.format(
                        user=member.name, userid=member.id, old=old, new=name))

        if reason:
            reason = reason.format(user=member.name)
            try:
                await client.send_message(member, reason)
            except discord.errors.Forbidden:
                await client.send_message(self.channel, '%s: %s' % (member.mention, reason))
