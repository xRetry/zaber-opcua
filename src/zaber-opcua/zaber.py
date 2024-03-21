from zaber_motion.ascii import Connection, Lockstep, Axis
from constants import *

def init_zaber() -> tuple[Lockstep, Axis]:
    connection = Connection.open_serial_port(ZABER_SERIAL_PORT)
    connection.enable_alerts()

    device_list = connection.detect_devices()

    controller_parallel = device_list[0]
    controller_cross = device_list[1]

    lockstep = controller_parallel.get_lockstep(1)
    if lockstep.is_enabled():
        lockstep.disable()

    controller_parallel.all_axes.home()
    controller_cross.all_axes.home()

    lockstep.enable(1, 2)
    axis_cross = controller_cross.get_axis(1)

    return (lockstep, axis_cross)

if __name__ == "__main__":
    pass
