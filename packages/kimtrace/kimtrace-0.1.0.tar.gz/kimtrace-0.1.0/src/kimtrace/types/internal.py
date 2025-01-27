from dataclasses import dataclass
from typing import Any, List
from datetime import datetime
from .external import KRunData

@dataclass
class KRunDataScope:
    context: KRunData
    caller: str

@dataclass
class HandleKRunSuccessParams:
    response: Any
    redactors: List[str]
    context: KRunData
    startTime: datetime
    endTime: datetime

@dataclass
class HandleKRunErrorParams:
    error: Exception
    context: KRunData
    startTime: datetime
    endTime: datetime

@dataclass
class HandleKStepSuccessParams:
    response: Any
    stepName: str
    args: str
    redactors: List[str]
    context: KRunData
    startTime: datetime
    endTime: datetime
    calledFrom: str
    id: str

@dataclass
class HandleKStepErrorParams:
    error: Exception
    stepName: str
    args: str
    context: KRunData
    startTime: datetime
    endTime: datetime
    calledFrom: str
    id: str
