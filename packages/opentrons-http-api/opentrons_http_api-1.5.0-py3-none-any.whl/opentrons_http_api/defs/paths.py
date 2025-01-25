from dataclasses import dataclass


@dataclass(frozen=True)
class Paths:
    """
    HTTP API paths.
    """
    # v1

    # NETWORKING

    # CONTROL
    IDENTIFY = '/identify'
    ROBOT_LIGHTS = '/robot/lights'

    # SETTINGS
    SETTINGS = '/settings'
    SETTINGS_ROBOT = '/settings/robot'

    # DECK CALIBRATION
    CALIBRATION_STATUS = '/calibration/status'

    # MODULES

    # PIPETTES

    # MOTORS
    MOTORS_ENGAGED = '/motors/engaged'
    MOTORS_DISENGAGE = '/motors/disengage'

    # CAMERA

    # LOGS

    # HEALTH
    HEALTH = '/health'

    # RUN MANAGEMENT
    RUNS = '/runs'
    RUNS_RUN_ID = '/runs/{run_id}'
    RUNS_RUN_ID_COMMANDS = '/runs/{run_id}/commands'
    RUNS_RUN_ID_COMMANDS_COMMAND_ID = '/runs/{run_id}/commands/{command_id}'
    RUNS_RUN_ID_ACTIONS = '/runs/{run_id}/actions'
    RUNS_RUN_ID_LABWARE_OFFSETS = '/runs/{run_id}/labware_offsets'
    RUNS_RUN_ID_LABWARE_DEFINITIONS = '/runs/{run_id}/labware_definitions'
    RUNS_RUN_ID_LOADED_LABWARE_DEFINITIONS = '/runs/{run_id}/loaded_labware_definitions'

    # MAINTENANCE RUN MANAGEMENT

    # PROTOCOL MANAGEMENT
    PROTOCOLS = '/protocols'
    PROTOCOLS_PROTOCOL_ID = '/protocols/{protocol_id}'
    PROTOCOLS_PROTOCOL_ID_ACTIONS = '/protocols/{protocol_id}/actions'

    # SIMPLE COMMANDS
    COMMANDS = '/commands'
    COMMANDS_COMMAND_ID = '/commands/{command_id}'

    # DECK CONFIGURATION

    # ATTACHED MODULES

    # ATTACHED INSTRUMENTS

    # SESSION MANAGEMENT
    SESSIONS = '/sessions'

    # LABWARE CALIBRATION MANAGEMENT

    # PIPETTE OFFSET CALIBRATION MANAGEMENT

    # TIP LENGTH CALIBRATION MANAGEMENT

    # SYSTEM CONTROL

    # SUBSYSTEM MANAGEMENT
