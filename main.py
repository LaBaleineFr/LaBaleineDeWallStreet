#!/usr/bin/env python
import asyncio
import importlib
import logging.config
import os.path
import sys
from baleine import bot, conf, util

logger = logging.Logger(__name__)
logging.basicConfig(level=logging.INFO)

def main(settings_path, token):
    """ Bot entry point """

    # Make sure settings and plugins are all loaded, setup logging
    conf.load(settings_path)
    if hasattr(conf.settings, 'logging'):
        logging.config.dictConfig(conf.settings.logging)
    for module in conf.settings.modules:
        importlib.import_module(module)

    loop = asyncio.get_event_loop()
    try:
        # Run the bot
        mainbot = bot.Bot(conf.settings, loop=loop)
        try:
            loop.run_until_complete(mainbot.start(token))
        except KeyboardInterrupt:
            pass
        loop.run_until_complete(mainbot.logout())

    except Exception as exc:
        # In debug mode, let the exception through (to potential debugger), otherwise log it normally
        if conf.settings.debug:
            raise
        logger.exception('aborting bot')
        return 2

    finally:
        # Notify all tasks we are shutting down and try our best to let them complete
        pending = asyncio.Task.all_tasks(loop=loop)
        gathered = asyncio.gather(*pending, loop=loop)
        try:
            gathered.cancel()
            loop.run_until_complete(gathered)
            gathered.exception()                    # let them throw to avoid spurious warnings
        except:
            pass
        loop.run_until_complete(asyncio.sleep(0))   # let aiohttp connections disconnect
        util.http_session().close()                 # free up http session resources
        loop.close()                                # job done
        logging.shutdown()
    return 0


if __name__ == '__main__':
    # Load environment variables
    settings_path = os.environ.get('SETTINGS')
    if not settings_path:
        logger.critical('Environment variable SETTINGS missing')
        sys.exit(1)
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        logger.critical('Environment variable DISCORD_TOKEN missing')
        sys.exit(1)

    sys.exit(main(settings_path, token))
