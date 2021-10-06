from dataclasses import dataclass, field
from keyword import kwlist
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class Config:
    type_hooks: Dict[Type, Callable[[Any], Any]] = field(default_factory=dict)
    cast: List[Type] = field(default_factory=list)
    forward_references: Optional[Dict[str, Any]] = None
    check_types: bool = True
    strict: bool = False
    strict_unions_match: bool = False
    rename_map: Dict[str, str] = field(default_factory=lambda: {f"{k}_": k for k in kwlist})
