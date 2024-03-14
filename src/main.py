from zaber_motion import Units
from zaber_motion.ascii import Connection

PORT = '/dev/ttyACM0'

def main():
    with Connection.open_serial_port(PORT) as connection:
        connection.enable_alerts()

        device_list = connection.detect_devices()
        print("Found {} devices".format(len(device_list)))

        device_back = device_list[1]
        device_front = device_list[0]

        lockstep = device_front.get_lockstep(1)
        if lockstep.is_enabled():
            lockstep.disable()

        device_front.all_axes.home()
        device_back.all_axes.home()

        lockstep.enable(1, 2)

        axis_back = device_back.get_axis(1)

        # Move to 10mm
        lockstep.move_absolute(0, Units.LENGTH_MILLIMETRES, wait_until_idle=False)
        axis_back.move_absolute(0, Units.LENGTH_MILLIMETRES, wait_until_idle=False)

        axis_back.wait_until_idle()
        lockstep.wait_until_idle()

        lockstep.move_absolute(50, Units.LENGTH_MILLIMETRES, wait_until_idle=False)
        axis_back.move_absolute(50, Units.LENGTH_MILLIMETRES, wait_until_idle=False)

        lockstep.wait_until_idle()
        axis_back.wait_until_idle()


if __name__ == '__main__':
    main()
