import asyncio
import logging
from asyncua import Server, ua

from constants import *
from slide_actions import *
#from zaber import init_zaber
from zaber_dummy import init_zaber


async def run_opcua_server():
    slide_parallel, slide_cross = init_zaber()

    logging.basicConfig(level=LOG_LEVEL)
    _logger = logging.getLogger(__name__)

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://{OPCUA_IP}:{OPCUA_PORT}/opcua/")

    idx = await server.register_namespace(OPCUA_NAMESPACE)

    var_slide_parallel_pos, var_slide_parallel_busy = await init_slide_object(
        server=server, 
        idx=idx, 
        name="Parallel Slide", 
        slide=slide_parallel
    )
    var_slide_cross_pos, var_slide_cross_busy = await init_slide_object(
        server=server, 
        idx=idx, 
        name="Cross Slide", 
        slide=slide_cross
    )

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(OPCUA_REFRESH_TIME)

            await server.write_attribute_value(
                var_slide_parallel_pos.nodeid, 
                ua.DataValue(slide_long.get_position()) # pyright: ignore
            )

            await server.write_attribute_value(
                var_slide_parallel_busy.nodeid, 
                ua.DataValue(slide_parallel.is_busy()) # pyright: ignore
            )

            await server.write_attribute_value(
                var_slide_cross_pos.nodeid, 
                ua.DataValue(slide_cross.get_position()) # pyright: ignore
            )

            await server.write_attribute_value(
                var_slide_cross_busy.nodeid, 
                ua.DataValue(slide_cross.is_busy()) # pyright: ignore
            )

if __name__ == "__main__":
    pass
