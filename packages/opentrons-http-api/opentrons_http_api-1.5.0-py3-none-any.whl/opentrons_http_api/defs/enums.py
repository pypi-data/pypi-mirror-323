from __future__ import annotations
from enum import Enum


class SettingId(str, Enum):
    SHORT_FIXED_TRASH = 'shortFixedTrash'
    DECK_CALIBRATION_DOTS = 'deckCalibrationDots'
    DISABLE_HOME_ON_BOOT = 'disableHomeOnBoot'
    USE_OLD_ASPIRATION_FUNCTIONS = 'useOldAspirationFunctions'
    ENABLE_DOOR_SAFETY_SWITCH = 'enableDoorSafetySwitch'
    DISABLE_FAST_PROTOCOL_UPLOAD = 'disableFastProtocolUpload'


class Axis(str, Enum):
    X = 'x'
    Y = 'y'
    Z_L = 'z_l'
    Z_R = 'z_r'
    Z_G = 'z_g'
    P_L = 'p_l'
    P_R = 'p_r'
    Q = 'q'
    G = 'g'
    Z = 'z'
    A = 'a'
    B = 'b'
    C = 'c'


class Action(str, Enum):
    PLAY = 'play'
    PAUSE = 'pause'
    STOP = 'stop'


class EngineStatus(str, Enum):
    """
    Copied from opentrons.protocol_engine.types.EngineStatus.
    """
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED_BY_OPEN_DOOR = "blocked-by-open-door"
    STOP_REQUESTED = "stop-requested"
    STOPPED = "stopped"
    FINISHING = "finishing"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
