import asyncio
import logging
from zaber_motion.ascii import Axis, Lockstep
from zaber_motion import Units
from asyncua import Server, ua

#from zaber import init_zaber
from zaber_test import init_zaber

REFRESH_RATE = 0.5

def set_pos_slide_cross(device: Axis, value: float):
    # TODO(marco): Don't execute always
    device.move_absolute(value, Units.LENGTH_MILLIMETRES, wait_until_idle=False)

def set_pos_slide_long(device: Lockstep, value: float):
    # TODO(marco): Don't execute always
    device.move_absolute(value, Units.LENGTH_MILLIMETRES, wait_until_idle=False)


async def run_opcua_server():
    slide_long, slide_cross = init_zaber()

    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(__name__)

    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/opcua/")

    # set up our own namespace, not really necessary but should as spec
    uri = "localhost"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    obj_slide_long = await server.nodes.objects.add_object(idx, "Longitudinal Slide")
    var_slide_long_pos = await obj_slide_long.add_variable(idx, "position", 6.7, ua.VariantType.Double)
    var_slide_long_pos_target = await obj_slide_long.add_variable(idx, "target position", 6.7)
    obj_slide_cross = await server.nodes.objects.add_object(idx, "Cross Slide")
    var_slide_cross_pos = await obj_slide_cross.add_variable(idx, "position", 0, ua.VariantType.Double)
    var_slide_cross_pos_target = await obj_slide_cross.add_variable(idx, "target position", 0)

    # Set MyVariable to be writable by clients
    await var_slide_long_pos_target.set_writable()
    await var_slide_cross_pos_target.set_writable()

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(REFRESH_RATE)

            new_pos_slide_long = await var_slide_long_pos_target.get_value()
            set_pos_slide_long(slide_long, new_pos_slide_long)

            new_pos_slide_cross = await var_slide_cross_pos_target.get_value()
            set_pos_slide_cross(slide_cross, new_pos_slide_cross)

            await server.write_attribute_value(
                var_slide_long_pos.nodeid, 
                ua.DataValue(slide_long.get_position())
            )

            await server.write_attribute_value(
                var_slide_cross_pos.nodeid, 
                ua.DataValue(slide_cross.get_position())
            )


if __name__ == "__main__":
    pass
