class Action: ON, OFF, TOGGLE = range(3)

import xbmcaddon
addon = xbmcaddon.Addon()

import os
import xbmc
profile_path = xbmc.translatePath(addon.getAddonInfo('profile'))
fifo = os.path.join(profile_path, 'fifo')
