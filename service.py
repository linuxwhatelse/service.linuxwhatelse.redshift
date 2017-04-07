import os
import sys
import threading

import xbmc

import redshift
import utils

from globs import Action
from globs import fifo
from globs import addon


rs = redshift.Redshift()

class Receiver():
    _active = threading.Event()

    _exit   = threading.Event()
    _exited = threading.Event()

    fifo = None
    callback = None

    def __init__(self, fifo_path, on_receive=None):
        self.fifo = fifo_path
        self.callback = on_receive

    def _runner(self):
        if not self.callback or not hasattr(self.callback, '__call__'):
            return

        if os.path.exists(self.fifo):
            os.remove(self.fifo)

        try:
            os.mkfifo(self.fifo)
        except:
            utils.log('Unable to create fifo', lvl=xbmc.LOGERROR)
            return

        self._active.set()
        self._exited.clear()
        while not self._exit.is_set():
            with open(self.fifo) as fifo:
                line = fifo.read()

                if line == 'exit':
                    break

                self.callback(line) 

        try:
            os.remove(self.fifo)
        except:
            utils.log('Failed unlinking fifo', lvl=xbmc.LOGERROR)

        self._active.clear()
        self._exited.set()

    def send(self, msg):
        with open(self.fifo, 'a') as fifo:
            fifo.write(str(msg))

    def start(self):
        t = threading.Thread(target=self._runner)
        t.daemon = True
        t.start()

        return self._active.wait(1)

    def stop(self):
        self._exit.set()
        self._exit.wait()

        self.send('exit')
        self._exited.wait()

def do(action):
    try:
        action = int(action)
    except:
        utils.log('Unsupported action:', action)
        return

    if action == Action.ON:
        if rs.is_running:
            utils.log('Was on already!')
            utils.notify(utils.translate(30013))
            return

        utils.log('Turning on!')
        utils.notify(utils.translate(30012))

        # Reconfigure for setting changes to take effect
        configure_redshift(rs)
        rs.start()

    elif action == Action.OFF:
        if not rs.is_running:
            utils.log('Was off already!')
            utils.notify(utils.translate(30015))
            return

        utils.log('Turning off!')
        utils.notify(utils.translate(30014))
        rs.stop()
        rs.reset()

    elif action == Action.TOGGLE:
        if not rs.is_running:
            do(Action.ON)

        else:
            do(Action.OFF)

def configure_redshift(rs):
    rs.latitude  = float(addon.getSetting('latitude'))
    rs.longitude = float(addon.getSetting('longitude'))

    rs.transition = addon.getSetting('transition') == 'true'

    rs.temperature_day = addon.getSetting('day.temperature')
    rs.temperature_night = addon.getSetting('night.temperature')

    rs.brightness_day = float(addon.getSetting('day.brightness'))
    rs.brightness_night = float(addon.getSetting('night.brightness'))

    rs.gamma_day_r = float(addon.getSetting('day.gamma.r'))
    rs.gamma_day_g = float(addon.getSetting('day.gamma.g'))
    rs.gamma_day_b = float(addon.getSetting('day.gamma.b'))

    #rs.gamma_night_r = float(addon.getSetting('night.gamma.r'))
    #rs.gamma_night_g = float(addon.getSetting('night.gamma.g'))
    #rs.gamma_night_b = float(addon.getSetting('night.gamma.b'))


if __name__ == '__main__':
    recv = Receiver(fifo, do)
    if not recv.start():
        utils.log('Unable to start receiver pipe, exiting!')
        sys.exit(1)

    configure_redshift(rs)
    if not rs.start():
        utils.notify(utils.translate(30019))

        recv.stop()
        sys.exit(1)

    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(60):
            break

    recv.stop()

    rs.stop()
    rs.reset()

