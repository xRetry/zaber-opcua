from typing import Union
from zaber_motion import Units
from zaber_motion.ascii import Axis, Lockstep

def slide_move_absolute(_, axis: Union[Lockstep, Axis], value: float) -> bool:
    try:
        axis.stop()
        axis.move_absolute(value, Units.LENGTH_MILLIMETRES, wait_until_idle=False)
    except:
        return False
    return True

def slide_move_velocity(_, axis: Union[Lockstep, Axis], value: float) -> bool:
    try:
        axis.stop()
        axis.move_velocity(value, Units.VELOCITY_METRES_PER_SECOND, wait_until_idle=False)
    except:
        return False
    return True

def slide_stop(_, axis: Union[Lockstep, Axis]) -> bool:
    try:
        axis.stop()
    except:
        return False
    return True

def slide_move_max(_, axis: Union[Lockstep, Axis]) -> bool:
    try:
        axis.move_max()
    except:
        return False
    return True

def slide_move_min(_, axis: Union[Lockstep, Axis]) -> bool:
    try:
        axis.move_min()
    except:
        return False
    return True

