import json

import xbmc
import xbmcaddon
import xbmcgui

from globs import addon

def log(*args, **kwargs):
    if not kwargs or 'lvl' not in kwargs:
        lvl = xbmc.LOGNOTICE

    else:
        lvl = kwargs['lvl']

    msg = '[%s] ' % addon.getAddonInfo('name')
    msg += ' '.join(str(x) for x in args)

    xbmc.log(msg, level=lvl)

def notify(message, title=None, icon=None, display_time=2000, sound=False):
    if not title:
        title = addon.getAddonInfo('name')

    if not icon:
        icon = addon.getAddonInfo('icon')

    xbmcgui.Dialog().notification(title, message, icon, display_time, sound)

def translate(id):
    return addon.getLocalizedString(id)
