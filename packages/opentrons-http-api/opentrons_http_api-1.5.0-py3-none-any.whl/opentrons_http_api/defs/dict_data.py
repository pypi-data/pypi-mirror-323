"""
Dataclasses for easier creation and handling of data usually represented by a dict. Some classes with nested dicts also
provide a property representing the nested dict as a class, with a trailing underscore following its name.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Union

from opentrons_http_api.defs.enums import EngineStatus


@dataclass(frozen=True)
class _DictData:
    def dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Status(_DictData):
    status: EngineStatus

    @property
    def is_idle(self) -> bool:
        """
        Returns True iff the run has not yet started (assuming the status is up to date).
        """
        return self.status is EngineStatus.IDLE

    @property
    def is_active(self) -> bool:
        """
        Returns True iff the run was started but has not yet completely stopped.
        """
        return self.status in (
            EngineStatus.RUNNING,
            EngineStatus.PAUSED,
            EngineStatus.BLOCKED_BY_OPEN_DOOR,
            EngineStatus.STOP_REQUESTED,
            EngineStatus.FINISHING,
        )

    @property
    def is_ending(self) -> bool:
        """
        Returns True iff the run is ending.
        """
        return self.status in (
            EngineStatus.STOP_REQUESTED,
            EngineStatus.FINISHING,
        )

    @property
    def is_done(self) -> bool:
        """
        Returns True iff the run was started and has completely stopped.
        """
        return self.status in (
            EngineStatus.STOPPED,
            EngineStatus.FAILED,
            EngineStatus.SUCCEEDED,
        )


@dataclass(frozen=True)
class Error(_DictData):
    id: str
    createdAt: str
    errorCode: str
    errorType: str
    detail: str
    errorInfo: dict
    wrappedErrors: list[dict]


@dataclass(frozen=True)
class Vector(_DictData):
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class LabwareOffset(_DictData):
    id: str
    createdAt: str
    definitionUri: str
    location: dict[str, str]
    vector: dict[str, float]

    @property
    def slotName(self) -> str:
        return self.location['slotName']

    @property
    def vector_(self) -> Vector:
        return Vector(**self.vector)

    @staticmethod
    def create(definitionUri: str, location: dict[str, str], vector: Union[dict[str, float], Vector]) -> LabwareOffset:
        """
        Create a user defined labware offset where id and createdAt are not known.
        """
        if isinstance(vector, Vector):
            vector = vector.dict()

        return LabwareOffset(id='', createdAt='', definitionUri=definitionUri, location=location, vector=vector)


@dataclass(frozen=True)
class Setting(_DictData):
    id: str
    old_id: str
    title: str
    description: str
    restart_required: bool
    value: bool


@dataclass(frozen=True)
class RobotSettings(_DictData):
    model: str
    name: str
    version: int
    gantry_steps_per_mm: dict
    acceleration: dict
    serial_speed: int
    default_pipette_configs: dict
    default_current: dict
    low_current: dict
    high_current: dict
    default_max_speed: dict
    log_level: str
    z_retract_distance: int
    left_mount_offset: list[int]


@dataclass(frozen=True)
class HealthInfo(_DictData):
    name: str
    robot_model: str
    api_version: str
    fw_version: str
    board_revision: str
    logs: list[str]
    system_version: str
    maximum_protocol_api_version: list[int]
    minimum_protocol_api_version: list[int]
    robot_serial: str
    links: dict[str, str]


@dataclass(frozen=True)
class RunInfo(_DictData):
    id: str
    createdAt: str
    status: str
    current: bool
    actions: list[dict]
    errors: list[dict]
    pipettes: list[dict]
    modules: list[dict]
    labware: list[dict]
    liquids: list[dict]
    labwareOffsets: list[dict]
    protocolId: str
    completedAt: Optional[str] = None
    startedAt: Optional[str] = None

    @property
    def status_(self) -> Status:
        return Status(EngineStatus(self.status))

    @property
    def errors_(self) -> list[Error]:
        return [Error(**error)
                for error in self.errors]

    @property
    def labwareOffsets_(self) -> list[LabwareOffset]:
        return [LabwareOffset(**offset)
                for offset in self.labwareOffsets]


@dataclass(frozen=True)
class ProtocolInfo(_DictData):
    id: str
    createdAt: str
    files: list[dict]
    protocolType: str
    robotType: str
    metadata: dict
    analyses: list
    analysisSummaries: list[dict]
