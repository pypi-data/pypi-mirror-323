"""Aibaba AI **Runnable** and the **Aibaba AI Expression Language (LCEL)**.

The Aibaba AI Expression Language (LCEL) offers a declarative method to build
production-grade programs that harness the power of LLMs.

Programs created using LCEL and Aibaba AI Runnables inherently support
synchronous, asynchronous, batch, and streaming operations.

Support for **async** allows servers hosting LCEL based programs to scale better
for higher concurrent loads.

**Batch** operations allow for processing multiple inputs in parallel.

**Streaming** of intermediate outputs, as they're being generated, allows for
creating more responsive UX.

This module contains schema and implementation of Aibaba AI Runnables primitives.
"""

from aibaba_ai_core.runnables.base import (
    Runnable,
    RunnableBinding,
    RunnableGenerator,
    RunnableLambda,
    RunnableMap,
    RunnableParallel,
    RunnableSequence,
    RunnableSerializable,
    chain,
)
from aibaba_ai_core.runnables.branch import RunnableBranch
from aibaba_ai_core.runnables.config import (
    RunnableConfig,
    ensure_config,
    get_config_list,
    patch_config,
    run_in_executor,
)
from aibaba_ai_core.runnables.fallbacks import RunnableWithFallbacks
from aibaba_ai_core.runnables.history import RunnableWithMessageHistory
from aibaba_ai_core.runnables.passthrough import (
    RunnableAssign,
    RunnablePassthrough,
    RunnablePick,
)
from aibaba_ai_core.runnables.router import RouterInput, RouterRunnable
from aibaba_ai_core.runnables.utils import (
    AddableDict,
    ConfigurableField,
    ConfigurableFieldMultiOption,
    ConfigurableFieldSingleOption,
    ConfigurableFieldSpec,
    aadd,
    add,
)

__all__ = [
    "chain",
    "AddableDict",
    "ConfigurableField",
    "ConfigurableFieldSingleOption",
    "ConfigurableFieldMultiOption",
    "ConfigurableFieldSpec",
    "ensure_config",
    "run_in_executor",
    "patch_config",
    "RouterInput",
    "RouterRunnable",
    "Runnable",
    "RunnableSerializable",
    "RunnableBinding",
    "RunnableBranch",
    "RunnableConfig",
    "RunnableGenerator",
    "RunnableLambda",
    "RunnableMap",
    "RunnableParallel",
    "RunnablePassthrough",
    "RunnableAssign",
    "RunnablePick",
    "RunnableSequence",
    "RunnableWithFallbacks",
    "RunnableWithMessageHistory",
    "get_config_list",
    "aadd",
    "add",
]
