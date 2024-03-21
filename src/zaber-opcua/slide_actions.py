from typing import Union, Tuple
from zaber_motion import Units
from zaber_motion.ascii import Axis, Lockstep
from asyncua.common.methods import uamethod
from asyncua import Server, ua, Node

def capture_exceptions(func, *args, **kwargs):
    def wrapper():
        try:
            func(*args, **kwargs)
        except Exception as e:
            return str(e)
        return 'Ok'

    return wrapper

@capture_exceptions
def slide_move_absolute(_, axis: Union[Lockstep, Axis], pos: float, vel: float, acc: float) -> None:
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

@capture_exceptions
def slide_move_relative(_, axis: Union[Lockstep, Axis], pos: float, vel: float, acc: float) -> None:
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

@capture_exceptions
def slide_move_velocity(_, axis: Union[Lockstep, Axis], vel: float, acc: float) -> None:
    axis.stop()
    axis.move_velocity(
        velocity=vel, 
        unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED
    )

@capture_exceptions
def slide_stop(_, axis: Union[Lockstep, Axis]) -> None:
    axis.stop()

@capture_exceptions
def slide_move_max(_, axis: Union[Lockstep, Axis], vel: float, acc: float) -> None:
    axis.stop()
    axis.move_max(
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

@capture_exceptions
def slide_move_min(_, axis: Union[Lockstep, Axis], vel: float, acc: float) -> None:
    axis.stop()
    axis.move_min(
        velocity=vel,
        velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        acceleration=acc,
        acceleration_unit=Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    )

async def init_slide_object(server: Server, idx: int, name: str, slide: Union[Axis, Lockstep]) -> Tuple[Node, Node]:
    obj = await server.nodes.objects.add_object(idx, name)

    await obj.add_method(
        idx, 
        "move_absolute", 
        uamethod(lambda parent, pos, vel=0, acc=0: slide_move_absolute(parent, slide, pos, vel, acc)),
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
        uamethod(lambda parent, pos, vel=0, acc=0: slide_move_relative(parent, slide, pos, vel, acc)),
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
        uamethod(lambda parent, vel, acc=0: slide_move_velocity(parent, slide, vel, acc)),
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
        uamethod(lambda parent: slide_stop(parent, slide)),
        [],
        [
            ua.Argument(
                Name=ua.String("status"),
                DataType=ua.NodeId(ua.ObjectIds.String), # pyright: ignore
                Description=ua.LocalizedText("The response status text"),
            ), 
        ]
    )
    
    var_pos = await obj.add_variable(
        nodeid=idx, 
        bname="position [mm]", 
        val=0, 
        varianttype=ua.VariantType.Double
    )

    var_busy = await obj.add_variable(
        nodeid=idx, 
        bname="is busy", 
        val=False, 
        varianttype=ua.VariantType.Boolean
    )

    return var_pos, var_busy

