import asyncio
import logging
from asyncua import Server, ua
from pynput import mouse

from settings import *
from slides import init_slide_cross, init_slide_parallel, SlideNode

toggle_recording = False

def handle_mouse_click(x, y, button, pressed):
    global toggle_recording
    if pressed:
        print('pressed')
        toggle_recording = not toggle_recording

async def run_opcua_server():
    logging.basicConfig(level=OPCUA_LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.debug("Initializing OPC-UA server")

    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://{OPCUA_IP}:{OPCUA_PORT}/")

    idx = await server.register_namespace(OPCUA_NAMESPACE)

    logger.debug("OPC-UA server successfully initialized")

    slide_parallel = await SlideNode.new(server, idx, "Parallel Slide", init_slide_parallel, logger)
    slide_cross = await SlideNode.new(server, idx, "Cross Slide", init_slide_cross, logger)

    logger.debug("Initializing mouse listener")

    listener = mouse.Listener(
        on_click=handle_mouse_click,
    )
    listener.start()

    logger.debug("Mouse listener successfully initialized")

    obj = await server.nodes.objects.add_object(idx, "Recording")
    var_is_recording = await obj.add_variable(
        nodeid=idx, 
        bname="is recording", 
        val=0, 
        varianttype=ua.VariantType.Boolean
    )

    logger.info("Init successful. Starting server...")

    last_toggle_recording = False
    async with server:
        while True:
            await asyncio.sleep(OPCUA_REFRESH_TIME)

            await slide_parallel.update_variables()
            await slide_cross.update_variables()

            # Only send if toggle has changed
            if last_toggle_recording != toggle_recording:
                await server.write_attribute_value(
                    var_is_recording.nodeid,
                    ua.DataValue(ua.Variant(True, ua.VariantType.Boolean))
                )
                last_toggle_recording = toggle_recording

if __name__ == "__main__":
    pass
