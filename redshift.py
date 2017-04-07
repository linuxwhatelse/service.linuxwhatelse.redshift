import os
import signal

import subprocess
import threading

import utils


class Redshift():
    __proc = None
    __lock = threading.RLock()
    __running = threading.Event()

    bin = '/usr/bin/redshift'

    brightness_day   = 1.0
    brightness_night = 1.0

    temperature_day   = '5700K'
    temperature_night = '3500K'

    gamma_day_r   = 0.8
    gamma_day_g   = 0.7
    gamma_day_b   = 0.8

    gamma_night_r = 0.6
    gamma_night_g = 0.6
    gamma_night_b = 0.6

    latitude  = 48.1
    longitude = 11.6

    latitude  = 48.3104110
    longitude = 12.2747260

    transition = True

    adjust_method = 'randr'
    screeen = 0


    @property
    def _command(self):
        cmd = [self.bin,
               '-b', '%s:%s' % (self.brightness_day, self.brightness_night),
               '-t', '%s:%s' % (self.temperature_day, self.temperature_night),
               '-l', '%s:%s' % (self.latitude, self.longitude),
               '-g', '%s:%s:%s' % (self.gamma_day_r, self.gamma_day_g, self.gamma_day_b),
               '-m', self.adjust_method
        ]

        if not self.transition:
            cmd.append('-r')

        return cmd

    @property
    def is_running(self):
        return self.__running.is_set()

    def __init__(self):
        pass

    def __get_pids(self):
        try:
            pids = map(int, subprocess.check_output(['pidof', self.bin]).split(' '))
        except subprocess.CalledProcessError:
            pids = None

        return pids

    def __start(self):
        pids = self.__get_pids()
        if pids:
            utils.log('Found running instances, trying to stop them.')
            try:
                for pid in pids:
                    os.kill(pid, signal.SIGINT)

            except OSError:
                utils.log('Unable to stop existing instances, bailing!')
                return

        with self.__lock:
            self.__proc = subprocess.Popen(self._command)

        self.__running.set()

        self.__proc.wait()

        self.__proc = None
        self.__running.clear()

    def start(self):
        t = threading.Thread(target=self.__start)
        t.daemon = True
        t.start()

        return self.__running.wait(1)

    def stop(self):
        if not self.is_running:
            return

        if not self.__proc:
            return

        with self.__lock:
            os.kill(self.__proc.pid, signal.SIGINT)
            self.__running.wait()

        self.reset()

    def restart(self):
        self.stop()
        self.start()

    def reset(self):
        subprocess.Popen([self.bin, '-x'])

