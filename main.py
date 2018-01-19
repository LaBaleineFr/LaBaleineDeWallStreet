#!/usr/bin/env python
import asyncio
import importlib
import logging
import os.path
import sys
from baleine import bot, conf, util

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

    loop = asyncio.get_event_loop()
    try:
        bot = bot.Bot(conf.settings, loop=loop)
        try:
            loop.run_until_complete(bot.start(token))
        except KeyboardInterrupt:
            pass
        loop.run_until_complete(bot.logout())
    except Exception as exc:
        if conf.settings.debug:
            raise
        logger.critical('%s', exc)
        sys.exit(2)
    finally:
        pending = asyncio.Task.all_tasks(loop=loop)
        gathered = asyncio.gather(*pending, loop=loop)
        try:
            gathered.cancel()
            loop.run_until_complete(gathered)
            gathered.exception()
        except:
            pass
        loop.run_until_complete(asyncio.sleep(0))
        util.http_session().close()
        loop.close()
