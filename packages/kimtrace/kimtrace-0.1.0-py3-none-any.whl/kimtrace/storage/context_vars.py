from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional
from ..types.external import KRunData

@dataclass
class KRunStorageData:
    context: KRunData
    caller: str

storage: ContextVar[Optional[KRunStorageData]] = ContextVar('krun_storage_data', default=None)
