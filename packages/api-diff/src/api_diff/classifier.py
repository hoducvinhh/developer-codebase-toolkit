"""Breaking change classification models and rules."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class ChangeCategory(str, Enum):
    BREAKING = "breaking"
    POTENTIALLY_BREAKING = "potentially_breaking"
    NON_BREAKING = "non_breaking"
    INFORMATIONAL = "informational"


class ApiChange(BaseModel):
    category: ChangeCategory
    path: str
    method: Optional[str] = None
    change_type: str
    message: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
