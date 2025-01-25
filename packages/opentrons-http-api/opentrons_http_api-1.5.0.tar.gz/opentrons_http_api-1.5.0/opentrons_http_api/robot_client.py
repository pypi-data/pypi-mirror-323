from __future__ import annotations
from typing import Tuple, BinaryIO, Optional, Sequence, Union

from opentrons_http_api.api import API
from opentrons_http_api.defs.dict_data import LabwareOffset, Setting, RobotSettings, HealthInfo, RunInfo, ProtocolInfo
from opentrons_http_api.defs.enums import SettingId, Action


class RobotClient:
    """
    Robot client interface that utilises the Opentrons HTTP API.
    """
    def __init__(self, host: str = 'localhost'):
        self._api = API(host)

    def identify(self, seconds: int) -> None:
        self._api.post_identify(seconds)

    def lights(self) -> bool:
        return self._api.get_robot_lights()['on']

    def set_lights(self, on: bool) -> None:
        self._api.post_robot_lights(on)

    def settings(self) -> Tuple[Setting, ...]:
        d = self._api.get_settings()
        return tuple(Setting(**setting)
                     for setting in d['settings'])

    def set_setting(self, id_: Union[str, SettingId], value: bool) -> None:
        if isinstance(id_, SettingId):
            id_ = id_.value

        self._api.post_settings(id_, value)

    def robot_settings(self) -> RobotSettings:
        d = self._api.get_robot_settings()
        return RobotSettings(**d)

    def health(self) -> HealthInfo:
        info = self._api.get_health()
        return HealthInfo(**info)

    def runs(self) -> Tuple[RunInfo, ...]:
        d = self._api.get_runs()
        return tuple(RunInfo(**run_info)
                     for run_info in d['data'])

    def create_run(self, protocol_id: str,
                   labware_offsets: Optional[Union[Sequence[dict], Sequence[LabwareOffset]]] = None) -> RunInfo:
        if labware_offsets is None:
            labware_offsets = []

        # Get labware offsets as dicts
        else:
            if isinstance(labware_offsets[0], LabwareOffset):
                labware_offsets = [offset.dict() for offset in labware_offsets]

        data = {
            'protocolId': protocol_id,
            'labwareOffsets': labware_offsets,
        }
        d = self._api.post_runs(data)
        return RunInfo(**d['data'])

    def run(self, run_id: str) -> RunInfo:
        d = self._api.get_runs_run_id(run_id)
        return RunInfo(**d['data'])

    def action_run(self, run_id: str, action: Union[str, Action]) -> None:
        if isinstance(action, Action):
            action = action.value

        data = {
            'actionType': action
        }
        self._api.post_runs_run_id_actions(run_id, data)

    def protocols(self) -> Tuple[ProtocolInfo, ...]:
        d = self._api.get_protocols()
        return tuple(ProtocolInfo(**protocol_info)
                     for protocol_info in d['data'])

    def upload_protocol(self, protocol_file: BinaryIO,
                        labware_definitions: Optional[Sequence[BinaryIO]] = None) -> ProtocolInfo:
        """
        Upload a protocol with optional labware definitions to the robot.
        :param protocol_file: A Python or JSON protocol binary file object.
        :param labware_definitions: An optional sequence of JSON labware definition binary file objects, only if the
        protocol_file is in Python format.
        :return: ProtocolInfo object containing information about the protocol.
        """
        files = (protocol_file, ) if labware_definitions is None else (protocol_file, *labware_definitions)

        d = self._api.post_protocols(files)
        return ProtocolInfo(**d['data'])
