#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
""" Main entry point for the bot

TODO :
- configuration file
- much more refactor
- better exception handling w/ custom response messages
"""

import discord
import os
from chart import Chart
from book import Book
from price import price, conv

# We pass chart & order as instances for future configuration options
chart = Chart()
book = Book()

client = discord.Client()
token = os.environ['DISCORD_TOKEN']

rules = ['\nQuelques règles du Discord de la Baleine :\n']
rules.append('- Pas de pubs sans une autorisation des admins\n')
rules.append('- Courtoisie et savoir-vivre\n')
rules.append('- Les calls **SANS ARGUMENT** seront suivis par un avertissement et ensuite un bannissement\n')
rules.append('- Pensez aux gens qui vont lire et mettez-vous à leur place\n')
rules.append('- Le flood et le troll sont interdits\n')
rules.append('- Les commandes de prix, conv, etc. du bot sont uniquement autorisées dans le chan #bot\n')
rules.append('- Les liens de parrainage sont interdits\n\n\n')
rules.append('Commande du bot :\n\n')
rules.append('\tBaleineDeWallStreet :\n')
rules.append('\tprix -> price (market) coin\n')
rules.append('\tconversion -> conv unité coin\n')
rules.append('\tgraph -> chart coin\n')
rules.append('\torder book -> book coin\n\n')
rules.append('Lexique :\n\n')
rules.append('\t!helpList \n')
rules.append('\t!help Recherche\n')
rules = ''.join(rules)


class Switch(object):
    """ Custom switch class """
    value = None

    def __new__(cls, value):
        cls.value = value
        return True


def case(*args):
    """ Custom case mimicked """
    return any((arg == Switch.value for arg in args))


def handle(query):
    res = ''
    query = query.lower()
    if len(query.split()) > 1:
        while Switch((query.split()[0]).lower()):
            if case('prix'):
                res = price(query.split())
                break
            if case('price'):
                res = price(query.split())
                break
            if case('conv'):
                res = conv(query.split())
                break
            if case('chart'):
                res = chart.chart(query.split()[1])
                break
            if case('book'):
                res = book.book(query.split()[1])
                break
            break
    return res


@client.event
async def on_message(message):


    # Auto clean
    if str(message.channel) == 'accueil':
        await client.delete_message(message)

    # Troll feature for novice using the bot in the wrong channel
    if message.content.startswith((
            'price',
            'Price',
            'prix',
            'Prix',
            'conv',
            'Conv',
            'chart',
            'Chart',
            'book',
            'Book')):
        if str(message.channel) != 'bot':
            roles = [i.name for i in message.author.roles]
            if 'Baleine novice' in roles:
                await client.send_message(message.author, 'Es-tu sûr de respecter les règles d\'utilisation du bot ?;)')

    if message.content.startswith((
            'price',
            'Price',
            'prix',
            'Prix')):
        await client.send_typing(message.channel)
        result = handle(message.content)
        for res in result:
            # TODO : we should change this strange way of handling multiple queries
            if res != '':
                await client.send_message(message.channel, res)

    if message.content.startswith((
            'conv',
            'Conv')):
        await client.send_typing(message.channel)
        await client.send_message(message.channel, handle(message.content))

    if message.content.startswith((
            'chart',
            'Chart')):
        await client.send_typing(message.channel)
        result = handle(message.content)
        await client.send_file(message.channel, result)
        if result.endswith('.png'):
            os.remove(result)            

    if message.content.startswith(('book', 'Book')):
        await client.send_typing(message.channel)
        result = handle(message.content)
        await client.send_file(message.channel, result)
        if result.endswith('.png'):
            os.remove(result)   

    if message.content.startswith((
            '/rules',
            '!rules',
            'rule',
            '!règles',
            'rules',
            'Rules')):
        await client.send_message(message.author, rules)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(token)
