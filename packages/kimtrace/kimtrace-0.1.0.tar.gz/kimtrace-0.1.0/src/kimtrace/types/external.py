from dataclasses import dataclass, field
from typing import Any, Optional, List
from datetime import datetime

@dataclass
class KStepData:
    id: str
    stepName: str
    stepStatus: str
    stepInput: Any
    stepOutput: Any
    stepStartTime: datetime
    stepEndTime: datetime
    calledFromId: str

    def to_dict(self):
        return {
            "id": self.id,
            "stepName": self.stepName,
            "stepStatus": self.stepStatus,
            "stepInput": self.stepInput,
            "stepOutput": self.stepOutput,
            "stepStartTime": self.stepStartTime.isoformat(),
            "stepEndTime": self.stepEndTime.isoformat(),
            "calledFromId": self.calledFromId
        }

@dataclass
class KRunData:
    id: str
    clientId: Optional[str] = None
    runName: str = ""
    runStatus: Optional[str] = None
    tags: Optional[List[str]] = field(default_factory=list)
    redactors: List[str] = field(default_factory=list)
    runInput: Optional[Any] = None
    runOutput: Optional[Any] = None
    steps: Optional[List[KStepData]] = field(default_factory=list)
    runStartTime: Optional[datetime] = None
    runEndTime: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "clientId": self.clientId,
            "runName": self.runName,
            "runStatus": self.runStatus,
            "tags": self.tags,
            "redactors": self.redactors,
            "runInput": self.runInput,
            "runOutput": self.runOutput,
            "steps": [step.to_dict() for step in self.steps] if self.steps else [],
            "runStartTime": self.runStartTime.isoformat() if self.runStartTime else None,
            "runEndTime": self.runEndTime.isoformat() if self.runEndTime else None
        }

class KStatus:
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class KStepParams:
    step_name: Optional[str] = None

@dataclass
class KRunParams:
    run_name: str
    run_id: Optional[str] = None
    emit_only_on_failure: Optional[bool] = False
    tags: Optional[List[str]] = field(default_factory=list)
    redactors: List[str] = field(default_factory=list)
