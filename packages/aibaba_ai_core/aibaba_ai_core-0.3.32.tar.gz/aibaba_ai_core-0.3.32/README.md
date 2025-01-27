# 🍎️ Aibaba AI Core Foundation

[![Downloads](https://static.pepy.tech/badge/aibaba_ai_core/month)](https://pepy.tech/project/aibaba_ai_core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install aibaba_ai_core
```

## Overview

Aibaba AI Core provides fundamental building blocks that serve as the foundation for the entire Aibaba AI ecosystem.

These foundational components are intentionally kept minimal and modular. They include essential abstractions for various components such as language models, document processing, embedding systems, vector databases, retrieval mechanisms, and more.

By establishing these standard interfaces, any provider can implement them and seamlessly integrate with the broader Aibaba AI ecosystem.

For comprehensive documentation, visit the [API reference](https://docs.aibaba.world/api_reference/core/index.html).

## 1️⃣ Primary Interface: Runnables

Runnables form the backbone of Aibaba AI Core. This interface is implemented by most components, providing:

- Unified execution methods (invoke, batch, stream, etc.)
- Built-in support for error handling, fallbacks, schemas, and runtime configuration
- Integration with Aibaba AI Build for deployment

Learn more in the [runnable documentation](https://docs.aibaba.world/docs/expression_language/interface). Key components implementing this interface include: LLMs, Chat Models, Prompts, Retrievers, Tools, and Output Parsers.

Two approaches to using Aibaba AI Core:

1. **Direct (Imperative)**: Straight function calls like `model.invoke(...)`

2. **Compositional (Declarative)**: Using Aibaba AI Expression Language (LCEL)

3. **Hybrid**: Combine both approaches by including custom functions within LCEL sequences

| Capability | Direct Method                  | Compositional Method |
| --------- | ------------------------------ | ------------------- |
| Code Style | Standard Python               | LCEL                |
| Tracing   | ✅ – Built-in                  | ✅ – Built-in       |
| Parallel  | ✅ – Via threads/coroutines    | ✅ – Automatic      |
| Streaming | ✅ – Through yield             | ✅ – Automatic      |
| Async     | ✅ – Using async/await         | ✅ – Automatic      |

## ⚡️ Understanding LCEL

Aibaba AI Expression Language (LCEL) is a declarative approach for combining Aibaba AI Core components into sequences or directed acyclic graphs (DAGs), addressing common LLM integration patterns.

LCEL sequences are automatically optimized for execution, featuring parallel processing, streaming capabilities, tracing, and asynchronous operations.

Explore more in the [LCEL documentation](https://docs.aibaba.world/docs/expression_language/).

For complex workflows requiring cycles or recursion, consider [LangGraph](https://github.com/aibaba-ailanggraph).

## 📕 Version Management

Current version: `0.1.x`

As the foundational layer of Aibaba AI, we maintain strict version control with advance notifications of changes. The `aibaba_ai_core.beta` module is exempt from this policy to allow rapid innovation.

Version increment guidelines:

Minor versions (0.x.0):
- Breaking changes to public APIs outside `aibaba_ai_core.beta`

Patch versions (0.0.x):
- Bug fixes
- Feature additions
- Internal interface changes
- `aibaba_ai_core.beta` modifications

## 💁 Community Participation

We actively encourage contributions to this open-source project, whether through new features, infrastructure improvements, or documentation enhancements.

See our [Contributing Guide](https://docs.aibaba.world/docs/contributing/) for details.

## ⛰️ Benefits of Aibaba AI Core

As the foundation for the entire Aibaba AI ecosystem, building on Aibaba AI Core offers several advantages:

- **Independent Components**: Built around provider-agnostic, standalone abstractions
- **Reliable API**: Committed to stable versioning with clear communication about changes
- **Production-Ready**: Extensively tested and widely deployed across the LLM ecosystem
- **Open Development**: Active community participation and contribution-friendly environment
