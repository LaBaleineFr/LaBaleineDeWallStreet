import os.path
import re
from baleine import command, conf, embed


class Help(command.Command):
    """ Bot command that shows an embed from a YAML file """
    name = 'help'

    errors = {
        'usage': 'Help on what?',
        'unknown': 'Je ne connais pas ce sujet',
    }

    async def execute(self, message, args):
        if len(args) != 1:
            await self.error('usage')
            return

        # We will use subject as file name, make sure it is safe
        subject = args[0]
        result = re.sub('[^a-zA-Z\d\. ]|( ){2,}','', subject)   # Keep letters, numbers dots and spaces
        if not result or os.path.splitext(result)[0].isspace():
            await self.error('unknown')
            return

        try:
            with open(os.path.join(conf.settings.help_path, subject + '.yml'), 'r') as fd:
                obj = embed.from_yaml(fd)
        except IOError:
            # The file does not exist, or is not readable
            await self.error('unknown')
            return

        await self.send('', embed=obj)
