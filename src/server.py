import asyncio
import logging
from asyncua import Server, ua
from asyncua.common.methods import uamethod
from zaber import Axis, Lockstep

from constants import *
from slide_actions import *
#from zaber import init_zaber
from zaber_test import init_zaber

async def init_slide_object(server: Server, idx: int, name: str, slide: Union[Axis, Lockstep]):
    obj = await server.nodes.objects.add_object(idx, name)
    var_pos = await obj.add_variable(idx, "position", 0, ua.VariantType.Double)

    await obj.add_method(
        idx, 
        "move_absolute", 
        uamethod(lambda parent, val: slide_move_absolute(parent, slide, val)),
        [ua.VariantType.Double],
        [ua.VariantType.Boolean]
    )
    await obj.add_method(
        idx, 
        "stop", 
        uamethod(lambda parent: slide_stop(parent, slide)),
        [],
        [ua.VariantType.Boolean]
    )
    return var_pos

async def run_opcua_server():
    slide_long, slide_cross = init_zaber()

    logging.basicConfig(level=LOG_LEVEL)
    _logger = logging.getLogger(__name__)

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:{OPCUA_PORT}/opcua/")

    idx = await server.register_namespace(OPCUA_NAMESPACE)

    var_slide_long_pos = await init_slide_object(server, idx, "Parallel Slide", slide_long)
    var_slide_cross_pos = await init_slide_object(server, idx, "Cross Slide", slide_cross)

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(OPCUA_REFRESH_TIME)

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
