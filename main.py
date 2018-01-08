#!/usr/bin/env python
import importlib
import logging
import os.path
import sys
import yaml

logger = logging.Logger(__name__)
logging.basicConfig(level=logging.INFO)

ROOT = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    sys.path.append(os.path.join(ROOT, 'baleine'))

    settings_path = os.environ.get('SETTINGS')
    if not settings_path:
        logger.critical('Environment variable SETTINGS missing')
        sys.exit(1)

    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        logger.critical('Environment variable DISCORD_TOKEN missing')
        sys.exit(1)

    with open(settings_path, 'r') as sf:
        settings = yaml.load(sf)

    for module in settings['modules']:
        importlib.import_module(module)

    from bot import Bot
    #try:
    Bot(settings).run(token)
    #except Exception as exc:
        #logger.critical('%s', exc)
        #sys.exit(2)
