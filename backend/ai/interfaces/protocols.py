"""
Structural protocols that AI stage implementations may optionally satisfy.

Using ``typing.Protocol`` (PEP 544) rather than ABCs keeps components loosely
coupled — any class with the right shape satisfies the protocol without
inheriting from it.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ILoadable(Protocol):
    """Component that lazily loads heavy resources (models, weights)."""

    async def load(self) -> None:
        """Load all required resources into memory."""
        ...

    async def unload(self) -> None:
        """Release all held resources."""
        ...

    @property
    def is_loaded(self) -> bool:
        """Return True when resources are ready."""
        ...


@runtime_checkable
class IProcessable(Protocol):
    """Component that processes input and returns output."""

    async def process(self, input: Any, context: Any) -> Any:
        """Execute the primary processing logic."""
        ...


@runtime_checkable
class ICacheable(Protocol):
    """Component whose results can be cached."""

    def cache_key(self, input: Any) -> str:
        """Return a deterministic cache key for the given input."""
        ...


@runtime_checkable
class IConfigurable(Protocol):
    """Component that can be reconfigured at runtime."""

    def configure(self, **kwargs: Any) -> None:
        """Apply configuration parameters."""
        ...

    def validate_config(self) -> bool:
        """Validate current configuration; raise ValueError on bad config."""
        ...


@runtime_checkable
class IStreamable(Protocol):
    """Component that can emit partial results during processing."""

    async def stream(self, input: Any, context: Any):  # type: ignore[return]
        """Yield partial results as they become available."""
        ...
