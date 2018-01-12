import importlib
import math

def import_string(path):
    try:
        module_path, name = path.rsplit('.', 1)
    except ValueError:
        raise ImportError('Invalid module path %r' % path)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, name)
    except AttributeError:
        raise ImportError('Module %r has no attribute %r' % (module_path, name))


COMMAS = {
    'USD': 2,
    'EUR': 2,
}

def format_price(value, ticker, hide_ticker=False):
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

