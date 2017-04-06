import xbmcgui

from globs import fifo
from globs import Action
from globs import addon

import utils

from service import Receiver


if __name__ == '__main__':
    cli_action = None
    if len(sys.argv) > 1:
        cli_action = sys.argv[1]


    action = None
    if cli_action == 'on':
        action = Action.ON

    elif cli_action == 'off':
        action = Action.OFF

    elif cli_action == 'toggle':
        action = Action.TOGGLE

    else:
        options = [utils.translate(30016),  # Toggle
                   utils.translate(30017),  # Turn on
                   utils.translate(30018)]  # Turn off

        res = xbmcgui.Dialog().select(addon.getAddonInfo('name'), options)

        if res == 0:
            action = Action.TOGGLE

        elif res == 1:
            action = Action.ON

        elif res == 2:
            action = Action.OFF


    if action is not None: Receiver(fifo).send(action)
