import asyncio
import logging
from zaber_motion.ascii import Axis, Lockstep
from zaber_motion import Units
from asyncua import Server, ua
from asyncua.common.methods import uamethod

#from zaber import init_zaber
from zaber_test import init_zaber

REFRESH_RATE = 0.5

def set_pos_slide(_, axis: Lockstep|Axis, value: float) -> bool:
    try:
        axis.stop()
        axis.move_absolute(value, Units.LENGTH_MILLIMETRES, wait_until_idle=False)
    except:
        return False
    return True

async def run_opcua_server():
    slide_long, slide_cross = init_zaber()
    set_pos_slide_long = uamethod(lambda parent, val: set_pos_slide(parent, slide_long, val))
    set_pos_slide_cross = uamethod(lambda parent, val: set_pos_slide(parent, slide_cross, val))

    logging.basicConfig(level=logging.DEBUG)
    _logger = logging.getLogger(__name__)

    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/opcua/")

    # set up our own namespace, not really necessary but should as spec
    uri = "localhost"
    idx = await server.register_namespace(uri)

    obj_slide_long = await server.nodes.objects.add_object(idx, "Longitudinal Slide")
    var_slide_long_pos = await obj_slide_long.add_variable(idx, "position", 6.7, ua.VariantType.Double)
    await obj_slide_long.add_method(
        idx, 
        "set_position", 
        set_pos_slide_long,
        [ua.VariantType.Double],
        [ua.VariantType.Boolean]
    )

    obj_slide_cross = await server.nodes.objects.add_object(idx, "Cross Slide")
    var_slide_cross_pos = await obj_slide_cross.add_variable(idx, "position", 0, ua.VariantType.Double)
    await obj_slide_cross.add_method(
        idx, 
        "set_position", 
        set_pos_slide_cross,
        [ua.VariantType.Double],
        [ua.VariantType.Boolean]
    )

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(REFRESH_RATE)

            await server.write_attribute_value(
                var_slide_long_pos.nodeid, 
                ua.DataValue(slide_long.get_position()) # pyright: ignore
            )

            await server.write_attribute_value(
                var_slide_cross_pos.nodeid, 
                ua.DataValue(slide_cross.get_position()) # pyright: ignore
            )

if __name__ == "__main__":
    pass
