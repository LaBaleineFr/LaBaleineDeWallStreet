import importlib
import math
import unicodedata

# ============================================================================

def import_string(path):
    """ Import a python object by its full python dotted path """
    try:
        module_path, name = path.rsplit('.', 1)
    except ValueError:
        raise ImportError('Invalid module path %r' % path)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, name)
    except AttributeError:
        raise ImportError('Module %r has no attribute %r' % (module_path, name))

# ============================================================================

def http_session():
    """ Return an http session to use for http requests """
    session = getattr(http_session, '_session', None)
    if session is None:
        import aiohttp
        session = http_session._session = aiohttp.ClientSession()
    return session

# ============================================================================

def find_channel(guild, text):
    """ Given a string that may be either a channel name or id, find the channel """
    try:
        idval = int(text)
    except ValueError:
        pass
    else:
        try:
            return next(filter(lambda chan: chan.id == idval, guild.channels))
        except StopIteration:
            pass
    try:
        text = text.lower()
        return next(filter(lambda chan: chan.name.lower() == text, guild.channels))
    except StopIteration:
        raise ValueError('Channel %s not found' % text)


def find_role(guild, text):
    """ Given a string that may be either a role name or id, find the role """
    try:
        idval = int(text)
    except ValueError:
        pass
    else:
        try:
            return next(filter(lambda role: role.id == idval, guild.roles))
        except StopIteration:
            pass
    try:
        text = text.lower()
        return next(filter(lambda role: role.name.lower() == text, guild.roles))
    except StopIteration:
        raise ValueError('Role %s not found' % text)

# ============================================================================

COMMAS = {'USD': 2, 'EUR': 2}

def format_price(value, ticker, hide_ticker=False):
    """ Clever display of prices """
    unit, commas = '', COMMAS.get(ticker, 3)

    if ticker == 'BTC' and value < 1:
        value, ticker, commas = value * 100000000, 'sats', 0

    absval = abs(value)

    if absval >= 100000000:
        value, commas, unit = value / 1000000, 0, 'M'
    elif absval >= 10000000:
        value, commas, unit = value / 1000000, 1, 'M'
    elif absval >= 100000:
        value, commas, unit = value / 1000, 0, 'k'
    elif absval >= 10000:
        value, commas, unit = value / 1000, 1, 'k'
    elif absval >= 100:
        commas = 0

    elif absval < 0.001:
        value, unit = value * 1000000, 'µ'
        commas += max(0, 1-math.floor(math.log10(absval)))
    elif absval < 0.1:
        commas += max(0, 1-math.floor(math.log10(absval)))

    return '{value:.{commas}f} {unit}{ticker}'.format(
        value=value,
        commas=commas,
        unit=unit,
        ticker='' if hide_ticker else ticker
    )

# ============================================================================

_TAGS = ('<font>', '<circle>', '<super>', '<sub>', '<vertical>',
         '<wide>', '<narrow>', '<small>', '<square>')

def simplify_unicode(text):
    decompose = unicodedata.decomposition
    result = []
    for char in text:
        dchar = decompose(char)
        if dchar:
            dchar = dchar.split()
            if dchar[0] in _TAGS and len(dchar) == 2:
                result.append(chr(int(dchar[1], 16)))
            else:
                result.append(char)
        else:
            result.append(char)
    return ''.join(result)
