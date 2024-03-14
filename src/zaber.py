from zaber_motion.ascii import Connection, Lockstep, Axis

SERIAL_PORT = '/dev/ttyACM0'

def init_zaber() -> tuple[Lockstep, Axis]:
    connection = Connection.open_serial_port(SERIAL_PORT)
    connection.enable_alerts()

    device_list = connection.detect_devices()

    device_long = device_list[0]
    device_cross = device_list[1]

    lockstep = device_long.get_lockstep(1)
    if lockstep.is_enabled():
        lockstep.disable()

    device_long.all_axes.home()
    device_cross.all_axes.home()

    lockstep.enable(1, 2)
    axis_cross = device_cross.get_axis(1)

    return (lockstep, axis_cross)

if __name__ == "__main__":
    pass
