import asyncio
import logging
from asyncua import Server

from settings import *
from slides import init_zaber, SlideNode

async def run_opcua_server():
    logging.basicConfig(level=OPCUA_LOG_LEVEL)
    _logger = logging.getLogger(__name__)

    _logger.debug("Initializing OPC-UA server")

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://{OPCUA_IP}:{OPCUA_PORT}/opcua/")

    idx = await server.register_namespace(OPCUA_NAMESPACE)

    _logger.info("OPC-UA server successfully initialized")

    axis_parallel, axis_cross = None, None
    try:
        axis_parallel, axis_cross = init_zaber()
    except Exception as e:
        _logger.error(e)

    slide_parallel = await SlideNode.new(server, idx, "Parallel Slide", axis_parallel)
    slide_cross = await SlideNode.new(server, idx, "Cross Slide", axis_cross)

    _logger.info("Init successful. Starting server.")

    async with server:
        while True:
            await asyncio.sleep(OPCUA_REFRESH_TIME)

            await slide_parallel.update_variables()
            await slide_cross.update_variables()

if __name__ == "__main__":
    pass
