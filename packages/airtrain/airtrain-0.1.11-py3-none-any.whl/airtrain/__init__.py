"""Airtrain - A platform for building and deploying AI agents with structured skills"""

__version__ = "0.1.11"

from .core.skills import Skill
from .core.schemas import InputSchema, OutputSchema
from .core.credentials import BaseCredentials

__all__ = ["Skill", "InputSchema", "OutputSchema", "BaseCredentials"]
