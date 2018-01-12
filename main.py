#!/usr/bin/env python
import importlib
import logging
import os.path
import sys
from baleine import bot, conf

logger = logging.Logger(__name__)
logging.basicConfig(level=logging.INFO)

ROOT = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    settings_path = os.environ.get('SETTINGS')
    if not settings_path:
        logger.critical('Environment variable SETTINGS missing')
        sys.exit(1)
    conf.load(settings_path)

    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        logger.critical('Environment variable DISCORD_TOKEN missing')
        sys.exit(1)

    for module in conf.settings.modules:
        importlib.import_module(module)

    try:
        bot = bot.Bot(conf.settings)
        bot.run(token)
    except Exception as exc:
        if conf.settings.debug:
            raise
        logger.critical('%s', exc)
        sys.exit(2)
