import os.path
import re
from baleine import command, conf, embed


class Help(command.Command):
    name = 'help'

    async def execute(self, message, args):
        if len(args) != 1:
            await self.error('Help on what?')
            return

        subject = args[0]
        result = re.sub('[^a-zA-Z\d\. ]|( ){2,}','', subject)
        if not result or os.path.splitext(result)[0].isspace():
            await self.error('Je ne connais pas ce sujet')
            return

        try:
            with open(os.path.join(conf.settings.help_path, subject + '.yml'), 'r') as fd:
                obj = embed.from_yaml(fd)
        except IOError:
            await self.error('Je ne connais pas ce sujet')
            return

        await self.send('', embed=obj)
