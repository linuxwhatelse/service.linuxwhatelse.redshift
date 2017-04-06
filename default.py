import globs
from service import Receiver

from globs import url
from globs import addon
from globs import mpr

recv = Receiver(globs.fifo)


@mpr.s_url('/on/')
def redshift_on():
    recv.send(globs.Action.ON)

@mpr.s_url('/off/')
def redshift_off():
    recv.send(globs.Action.OFF)

@mpr.s_url('/toggle/')
def redshift_toggle():
    recv.send(globs.Action.TOGGLE)


if __name__ == '__main__':
    mpr.call(url)
