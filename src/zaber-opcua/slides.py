from typing import Union, Optional, Callable
from zaber_motion import Units, ConnectionFailedException, ConnectionClosedException, TimeoutException
from zaber_motion.ascii import Axis, Connection, Lockstep
from asyncua.common.methods import uamethod
from asyncua import Server, ua, Node
from logging import Logger
import time

from settings import *

Slide = Optional[Union[Axis, Lockstep]]

# Only used within `init_connection`, to store connection state
_zaber_conn = None

def init_connection() -> Optional[Connection]:
    global _zaber_conn
    
    if _zaber_conn is not None and str(_zaber_conn) == 'Connection 1 (Closed)':
        _zaber_conn = None

    if _zaber_conn is None:
        try:
            _zaber_conn = Connection.open_serial_port(ZABER_SERIAL_PORT)
            _zaber_conn.enable_alerts()
        except Exception as e:
            _zaber_conn = None
            raise e
    return _zaber_conn

def init_slide_parallel() -> Optional[Lockstep]:
    conn = init_connection()
    if conn is None:
        raise Exception('Connection not initialized')

    device_list = conn.detect_devices()
    controller_parallel = device_list[0]
    lockstep = controller_parallel.get_lockstep(1)
    if lockstep.is_enabled():
        lockstep.disable()

    controller_parallel.all_axes.home()
    lockstep.enable(1, 2)

    return lockstep

def init_slide_cross() -> Optional[Axis]:
    conn = init_connection()
    if conn is None:
        return None

    device_list = conn.detect_devices()
    controller_cross = device_list[1]
    controller_cross.all_axes.home()
    axis_cross = controller_cross.get_axis(1)

    return axis_cross


def capture_exceptions(func, *args, **kwargs) -> ua.DataValue:
    try:
        func(*args, **kwargs)
    except Exception as e:
        return ua.DataValue(
            Value=ua.Variant(str(e), ua.VariantType.String),
            StatusCode_=ua.StatusCode(ua.StatusCodes.Bad), # pyright: ignore
        )
    return ua.DataValue(ua.Variant('Ok', ua.VariantType.String))

def slide_move_absolute(_, axis: Slide, pos: float, vel: float, acc: float) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()
    axis.move_absolute(
        position=pos, 
        unit=Units.LENGTH_MILLIMETRES, 
        wait_until_idle=False,
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

def slide_move_relative(_, axis: Slide, pos: float, vel: float, acc: float) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()
    axis.move_relative(
        position=pos, 
        unit=Units.LENGTH_MILLIMETRES, 
        wait_until_idle=False,
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

def slide_move_velocity(_, axis: Slide, vel: float, acc: float) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()
    axis.move_velocity(
        velocity=vel, 
        unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED
    )

def slide_stop(_, axis: Slide) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()

def slide_move_max(_, axis: Slide, vel: float, acc: float) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()
    axis.move_max(
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

def slide_move_min(_, axis: Slide, vel: float, acc: float) -> None:
    if axis is None:
        raise Exception('Axis not initialized!')
    axis.stop()
    axis.move_min(
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

class SlideNode:
    server: Server
    fn_init: Callable[[], Slide]
    axis: Slide
    logger: Logger
    node_status: Node
    node_position: Node
    node_busy: Node
    position: float
    busy: bool
    last_attempt: float

    @staticmethod
    async def new(server: Server, idx: int, name: str, fn_init: Callable[[], Slide], logger: Logger):
        node = SlideNode()
        node.axis = None # Gets initialized in event loop
        node.server = server
        node.position = 0
        node.busy = False
        node.last_attempt = -1e5
        node.fn_init = fn_init
        node.logger = logger

        obj = await server.nodes.objects.add_object(idx, name)

        await obj.add_method(
            idx, 
            "move_absolute", 
            uamethod(lambda parent, pos, vel=0, acc=0: 
                capture_exceptions(slide_move_absolute, parent, node.axis, pos, vel, acc)
            ),
            [
                ua.Argument(
                    Name=ua.String("absolute position [mm]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The absolute target position of the slide"),
                ), 
                ua.Argument(
                    Name=ua.String("velocity [mm/s]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement velocity (0 = max. speed)"),
                ), 
                ua.Argument(
                    Name=ua.String("acceleration [mm/s^2]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement acceleration (0 = max. accel)"),
                ), 
            ],
            [
                ua.Argument(
                    Name=ua.String("status"),
                    DataType=ua.NodeId(ua.ObjectIds.String), # pyright: ignore
                    Description=ua.LocalizedText("The response status text"),
                ), 
            ]
        )

        await obj.add_method(
            idx, 
            "move_relative", 
            uamethod(lambda parent, pos, vel=0, acc=0: 
                capture_exceptions(slide_move_relative, parent, node.axis, pos, vel, acc)
            ),
            [
                ua.Argument(
                    Name=ua.String("relative position [mm]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The relative target position of the slide"),
                ), 
                ua.Argument(
                    Name=ua.String("velocity [mm/s]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement velocity (0 = max. speed)"),
                ), 
                ua.Argument(
                    Name=ua.String("acceleration [mm/s^2]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement acceleration (0 = max. accel)"),
                ), 
            ],
            [
                ua.Argument(
                    Name=ua.String("status"),
                    DataType=ua.NodeId(ua.ObjectIds.String), # pyright: ignore
                    Description=ua.LocalizedText("The response status text"),
                ), 
            ]
        )

        await obj.add_method(
            idx, 
            "move_velocity", 
            uamethod(lambda parent, vel, acc=0: 
                capture_exceptions(slide_move_velocity, parent, node.axis, vel, acc)
            ),
            [
                ua.Argument(
                    Name=ua.String("velocity [mm/s]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement velocity"),
                ), 
                ua.Argument(
                    Name=ua.String("acceleration [mm/s^2]"),
                    DataType=ua.NodeId(ua.ObjectIds.Double), # pyright: ignore
                    Description=ua.LocalizedText("The movement acceleration (0 = max. accel)"),
                ), 
            ],
            [
                ua.Argument(
                    Name=ua.String("status"),
                    DataType=ua.NodeId(ua.ObjectIds.String), # pyright: ignore
                    Description=ua.LocalizedText("The response status text"),
                ), 
            ]
        )
        
        await obj.add_method(
            idx, 
            "stop", 
            uamethod(lambda parent: 
                capture_exceptions(slide_stop, parent, node.axis)
            ),
            [],
            [
                ua.Argument(
                    Name=ua.String("status"),
                    DataType=ua.NodeId(ua.ObjectIds.String), # pyright: ignore
                    Description=ua.LocalizedText("The response status text"),
                ), 
            ]
        )

        node.node_status = await obj.add_variable(
            nodeid=idx, 
            bname="status", 
            val='No connection' if node.axis is None else 'Ok', 
            varianttype=ua.VariantType.String
        )
        node.node_position = await obj.add_variable(
            nodeid=idx, 
            bname="position [mm]", 
            val=0, 
            varianttype=ua.VariantType.Double
        )
        node.node_busy = await obj.add_variable(
            nodeid=idx, 
            bname="busy", 
            val=False, 
            varianttype=ua.VariantType.Boolean
        )

        return node

    async def update_variables(self):
        """
        Updates the OPC-UA variables with the current axis values.
        Only writes to the variables if:
            - the axis is initialized
            - the value has changed
        """

        if self.axis is not None:
            try:
                busy = self.axis.is_busy()
                if busy != self.busy:
                    self.busy = busy
                    await self.server.write_attribute_value(
                        self.node_busy.nodeid, 
                        ua.DataValue(ua.Variant(self.busy, ua.VariantType.Boolean)) 
                    )

                pos = self.axis.get_position(Units.LENGTH_MILLIMETRES)
                if pos != self.position:
                    self.position = pos
                    await self.server.write_attribute_value(
                        self.node_position.nodeid,
                        ua.DataValue(ua.Variant(self.position, ua.VariantType.Double)) 
                    )
            except (TimeoutException, ConnectionClosedException, ConnectionFailedException) as e:
                self.logger.debug('Zaber disconnected: '+str(e))
                self.axis = None
                await self.server.write_attribute_value(
                    self.node_status.nodeid,
                    ua.DataValue(ua.Variant(str(e), ua.VariantType.String))
                )
            except Exception as e:
                await self.server.write_attribute_value(
                    self.node_status.nodeid,
                    ua.DataValue(ua.Variant(str(e), ua.VariantType.String))
                )
        else:
            cur_time = time.perf_counter()
            if cur_time - self.last_attempt > ZABER_RECONNECT_TIMEOUT:
                self.last_attempt = cur_time
                try:
                    self.logger.debug('Attempting Zaber init')
                    self.axis = self.fn_init()

                    await self.server.write_attribute_value(
                        self.node_status.nodeid,
                        ua.DataValue(ua.Variant('Ok', ua.VariantType.String))
                    )
                    self.logger.debug('Zaber init successful')

                except Exception as e:
                    self.logger.debug('Zaber init failed: '+str(e))
                    await self.server.write_attribute_value(
                        self.node_status.nodeid,
                        ua.DataValue(ua.Variant(str(e), ua.VariantType.String))
                    )

if __name__ == "__main__":
    pass
