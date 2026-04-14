from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResumeData:
    name: Optional[str]
    email: Optional[str]
    skills: List[str] = field(default_factory=list)