"""``langchain-core`` defines the base abstractions for the Aibaba AI ecosystem.

The interfaces for core components like chat models, LLMs, vector stores, retrievers,
and more are defined here. The universal invocation protocol (Runnables) along with
a syntax for combining components (Aibaba AI Expression Language) are also defined here.

No third-party integrations are defined here. The dependencies are kept purposefully
very lightweight.
"""

from importlib import metadata

from aibaba_ai_core._api import (
    surface_aiagentforce_beta_warnings,
    surface_aiagentforce_deprecation_warnings,
)

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""

surface_aiagentforce_deprecation_warnings()
surface_aiagentforce_beta_warnings()
