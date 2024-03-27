import asyncio
import logging
from asyncua import Server

from settings import *
from slides import zaber_init_functions, SlideNode

async def run_opcua_server():
    logging.basicConfig(level=OPCUA_LOG_LEVEL)
    _logger = logging.getLogger(__name__)

    _logger.debug("Initializing OPC-UA server")

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://{OPCUA_IP}:{OPCUA_PORT}/")

    idx = await server.register_namespace(OPCUA_NAMESPACE)

    _logger.debug("OPC-UA server successfully initialized")

    fn_init_parallel, fn_init_cross = zaber_init_functions()
    slide_parallel = await SlideNode.new(server, idx, "Parallel Slide", fn_init_parallel)
    slide_cross = await SlideNode.new(server, idx, "Cross Slide", fn_init_cross)

    _logger.info("Init successful. Starting server...")

    async with server:
        while True:
            await asyncio.sleep(OPCUA_REFRESH_TIME)

            await slide_parallel.update_variables()
            await slide_cross.update_variables()

if __name__ == "__main__":
    pass
