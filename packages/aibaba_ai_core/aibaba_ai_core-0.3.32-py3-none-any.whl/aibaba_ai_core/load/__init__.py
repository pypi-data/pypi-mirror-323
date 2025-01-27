"""**Load** module helps with serialization and deserialization."""

from aibaba_ai_core.load.dump import dumpd, dumps
from aibaba_ai_core.load.load import load, loads
from aibaba_ai_core.load.serializable import Serializable

__all__ = ["dumpd", "dumps", "load", "loads", "Serializable"]
