from __future__ import annotations

import logging
from collections.abc import Collection, Sequence
from contextvars import ContextVar, Token
from copy import copy
from dataclasses import dataclass, field
from types import TracebackType
from typing import ClassVar, Optional, Self, Type

from .exception import DiagnosticException, T
from .models import DiagnosticError, Loc


@dataclass
class _DiagnosticContext:
    """Holds current context of diagnostic collector."""

    self: Optional[DiagnosticContext] = None
    """DiagnosticContext that created this context."""

    prefix: Loc = field(default_factory=list)
    """Holds prefix for the errors within this context."""

    suffix: Loc = field(default_factory=list)
    """Holds suffix for the errors within this context."""

    parent: Optional[_DiagnosticContext] = None
    """Parent context of this context, if any. It is used to combine prefixes and suffixes to provide full location."""

    @property
    def full_prefix(self) -> Loc:
        """Full prefix of the context, including parent prefixes."""
        return self.parent.full_prefix + self.prefix if self.parent else self.prefix

    @property
    def full_suffix(self) -> Loc:
        """Full suffix of the context, including parent suffixes."""
        return self.suffix + self.parent.full_suffix if self.parent else self.suffix


class DiagnosticContext:
    """
    Serves as unified location context for subsequent diagnostics. Can be used as context manager or manually, but must be
    always used only within DiagnosticCollector context.
    """

    _collector_context: ClassVar[ContextVar[Optional["DiagnosticCollector"]]] = ContextVar[Optional["DiagnosticCollector"]](
        "DiagnosticContext._collector_context", default=None
    )
    _diagnostic_context: ClassVar[ContextVar[_DiagnosticContext]] = ContextVar[_DiagnosticContext](
        "DiagnosticContext._diagnostic_context",
        default=_DiagnosticContext(),  # noqa: B039
    )

    def __init__(
        self,
        *,
        prefix: Optional[Loc] = None,
        strip_prefix: Optional[Loc] = None,
        strip_prefixes: Optional[Collection[Loc]] = None,
        suffix: Optional[Loc] = None,
        strip_suffix: Optional[Loc] = None,
        strip_suffixes: Optional[Collection[Loc]] = None,
    ) -> None:
        """
        :param prefix: Add specified prefix to all errors in this collector.
        :param strip_prefix: Strip specified prefix from all errors in this collector, including errors from inner collectors.
        :param strip_prefixes: Strip specified prefixes from all errors in this collector, including errors from inner collectors
            (using this argument, you can specify multiple different prefixes to be stripped).
        :param suffix: Add specified suffix to all errors in this collector.
        :param strip_suffix: Strip specified suffix from all errors in this collector, including errors from inner collectors.
        :param strip_suffixes: Strip specified suffixes from all errors in this collector, including errors from inner collectors
            (using this argument, you can specify multiple different suffixes to be stripped).
        """
        if not isinstance(prefix, list) and prefix is not None:  # type: ignore[unreachable]  # mypy does not ensure runtime check
            raise AttributeError("Prefix must be a list of locations.")

        if not isinstance(suffix, list) and suffix is not None:  # type: ignore[unreachable]  # mypy does not ensure runtime check
            raise AttributeError("Suffix must be a list of locations.")

        self._init_context = _DiagnosticContext(
            prefix=prefix or [],
            suffix=suffix or [],
        )

        self.strip_prefixes = ([strip_prefix] if strip_prefix else []) + list(strip_prefixes or [])
        self.strip_suffixes = ([strip_suffix] if strip_suffix else []) + list(strip_suffixes or [])

        self._diagnostic_context_token: Optional[Token[_DiagnosticContext]] = None

    @property
    def collector(self) -> DiagnosticCollector:
        """
        Access the DiagnosticCollector this DiagnosticContext appends errors to. It is the first collector in the hierarchy
        of contexts.

        Exception is raised when used outside DiagnosticCollector context.
        """
        collector = DiagnosticContext._collector_context.get()

        # Test explicitely for None, as DiagnosticCollector contains __bool__ method which checks for presence of errors.
        if collector is None:
            raise AttributeError("DiagnosticContext must be used within DiagnosticCollector context.")

        return collector

    @property
    def context(self) -> _DiagnosticContext:
        """
        Access the current context of the diagnostic collector.
        """
        return DiagnosticContext._diagnostic_context.get()

    def _resolve_prefix_and_suffix(self, prefix: Optional[Loc] = None, suffix: Optional[Loc] = None) -> tuple[Loc, Loc]:
        """
        Resolve prefix and suffix for the error. Allows to overwrite last context's prefix and suffix by specifying it
        as arguments. Prefixes and suffixes from higher order contexts are preserved.
        :param prefix: Overwrite prefix from last context.
        :param suffix: Overwrite suffix from last context.
        :return: Combined prefix and suffix.
        """
        ctx = self.context

        self.collector.logger.debug(ctx)

        if ctx.self == self:
            if prefix is None:
                prefix = self._init_context.prefix

            if suffix is None:
                suffix = self._init_context.suffix

            if ctx.parent:
                parent_context = ctx.parent
                prefix = parent_context.full_prefix + (prefix or [])
                suffix = (suffix or []) + parent_context.full_suffix
        else:
            if ctx.parent:
                prefix = ctx.parent.full_prefix + (prefix or ctx.prefix)
                suffix = (suffix or ctx.suffix) + ctx.parent.full_suffix
            else:
                if prefix is None:
                    prefix = ctx.prefix

                if suffix is None:
                    suffix = ctx.suffix

        return prefix, suffix

    def _append(self, error: DiagnosticError, prefix: Optional[Loc] = None, suffix: Optional[Loc] = None) -> None:
        """
        Append error to diagnostics.
        :param error: Error to be appended.
        :param prefix: Prefix to prepend to error location.
        :param suffix: Suffix to append to error location.
        """
        if not isinstance(error, DiagnosticError):
            raise AttributeError("DiagnosticCollector can accept only DiagnosticErrors.")

        if self.strip_prefixes:
            for strip_prefix in self.strip_prefixes:
                if error.loc[0 : len(strip_prefix)] == strip_prefix:
                    error = error.model_copy(update={"loc": error.loc[len(strip_prefix) :]})
                    break

        if self.strip_suffixes:
            for strip_suffix in self.strip_suffixes:
                if error.loc[-len(strip_suffix) :] == strip_suffix:
                    error = error.model_copy(update={"loc": error.loc[: -len(strip_suffix)]})

        prefix, suffix = self._resolve_prefix_and_suffix(prefix, suffix)

        error = error.model_copy(update={"loc": prefix + error.loc + suffix})

        self.collector.logger.debug(" -> loc=%s", error.loc)

        self.collector.errors.append(error)

    def append(
        self, error: DiagnosticError, prefix: Optional[Loc] = None, suffix: Optional[Loc] = None, stacklevel: int = 0
    ) -> Self:
        """
        Append new error to the collector, optionally prefixing it with specified prefix or suffixing it with specified suffix.
        :param error: Error to be added.
        :param prefix: Prefix to be prepended before error's loc. If specified, overwrites class-level prefix.
        :param suffix: Suffix to be appended to error's loc. If specified, overwrites class-level suffix.
        :param stacklevel: Optional stacklevel for logging (default 0).
        :return: Self for chaining
        """
        if prefix and suffix:
            self.collector.logger.debug(
                "Appending error with prefix %s and suffix %s: %s", prefix, suffix, error, stacklevel=stacklevel + 2
            )
        elif prefix:
            self.collector.logger.debug("Appending error with prefix %s: %s", prefix, error, stacklevel=stacklevel + 2)
        elif suffix:
            self.collector.logger.debug("Appending error with suffix %s: %s", suffix, error, stacklevel=stacklevel + 2)
        else:
            self.collector.logger.debug("Appending error: %s", error, stacklevel=stacklevel + 2)

        self._append(error, prefix, suffix)

        return self

    def add(
        self, error: DiagnosticError, prefix: Optional[Loc] = None, suffix: Optional[Loc] = None, stacklevel: int = 0
    ) -> Self:
        """Alias for append()"""
        return self.append(error, prefix, suffix, stacklevel + 1)

    def include(
        self,
        other: DiagnosticCollector | DiagnosticException[T] | Sequence[DiagnosticError],
        prefix: Optional[Loc] = None,
        suffix: Optional[Loc] = None,
    ) -> Self:
        """
        Include errors from other diagnostic response, optionally prefixing errors with location.
        :param other: Other diagnostic to include.
        :param prefix: Error prefix. Overrides class-level prefix.
        :param suffix: Error suffix. Overrides class-level suffix.
        :return: Self for chaining
        """
        errors: list[DiagnosticError] = []

        if isinstance(other, DiagnosticCollector):
            if other == self:
                return self

            errors.extend(other.errors)

            # As errors are processed by including in this collector, clear errors from other, to avoid raising exception.
            other.errors = []
        elif isinstance(other, DiagnosticException):
            errors.extend(other.errors())
        elif not isinstance(other, Sequence):
            raise AttributeError(
                "DiagnosticCollector can accept only other DiagnosticCollectior, DiagnosticException or sequence of "
                "DiagnosticErrors."
            )
        else:
            errors.extend(other)

        for error in errors:
            if prefix and suffix:
                self.collector.logger.debug(
                    "Including error from nested diagnostics with prefix %s and suffix %s: %s", prefix, suffix, error
                )
            elif prefix:
                self.collector.logger.debug("Including error from nested diagnostics with prefix %s: %s", prefix, error)
            elif suffix:
                self.collector.logger.debug("Including error from nested diagnostics with suffix %s: %s", suffix, error)
            else:
                self.collector.logger.debug("Including error from nested diagnostics: %s", error)

            self._append(error, prefix, suffix)

        return self

    def __enter__(self) -> Self:
        parent_context = self.context

        self._diagnostic_context_token = self.__class__._diagnostic_context.set(
            _DiagnosticContext(
                self=self,
                prefix=self._init_context.prefix,
                suffix=self._init_context.suffix,
                parent=parent_context,
            )
        )

        self.collector.logger.debug("Entering diagnostic context %r", self.__class__._diagnostic_context.get())

        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        self.collector.logger.debug("Leaving diagnostic context %r", self.__class__._diagnostic_context.get())

        if self._diagnostic_context_token:
            self._diagnostic_context.reset(self._diagnostic_context_token)

    async def __aenter__(self) -> Self:
        """
        Async version of context manager. See __enter__().
        """
        return self.__enter__()

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Async version of context manager. See __exit__().
        """
        self.__exit__(exc_type, exc_val, exc_tb)


class DiagnosticCollector(DiagnosticContext):
    """
    Diagnostic collector, that catches errors. Can be used as context manager, then it raises automatically
    at the __exit__ of the with block. Or can be used manually without context manager, then just call
    self.raise_if_errors().

    Example:

    >>> with DiagnosticCollector() as diag:
    >>>     diag.append(DiagnosticError(loc=["somewhere"], msg="There was an error.", type="error"))
    >>> # Here, DiagnosticException is raised.

    Or:

    >>> diag = DiagnosticCollector()
    >>> diag.append(DiagnosticError(loc=["somewhere"], msg="There was an error.", type="error"))
    >>> diag.raise_if_errors()  # Here, DiagnosticException is raised.

    Diagnostic collectors can be nested, and errors from inner collectors are included in outer collector.
    """

    def __init__(
        self,
        *,
        prefix: Optional[Loc] = None,
        strip_prefix: Optional[Loc] = None,
        strip_prefixes: Optional[Collection[Loc]] = None,
        suffix: Optional[Loc] = None,
        strip_suffix: Optional[Loc] = None,
        strip_suffixes: Optional[Collection[Loc]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        :param prefix: Add specified prefix to all errors in this collector.
        :param strip_prefix: Strip specified prefix from all errors in this collector, including errors from inner collectors.
        :param strip_prefixes: Strip specified prefixes from all errors in this collector, including errors from inner collectors
            (using this argument, you can specify multiple different prefixes to be stripped).
        :param suffix: Add specified suffix to all errors in this collector.
        :param strip_suffix: Strip specified suffix from all errors in this collector, including errors from inner collectors.
        :param strip_suffixes: Strip specified suffixes from all errors in this collector, including errors from inner collectors
            (using this argument, you can specify multiple different suffixes to be stripped).
        """
        super().__init__(
            prefix=prefix,
            strip_prefix=strip_prefix,
            strip_prefixes=strip_prefixes,
            suffix=suffix,
            strip_suffix=strip_suffix,
            strip_suffixes=strip_suffixes,
        )

        # Set to true in raise_if_errors, to prevent doubling of errors when context manager catches own exception.
        self._raised_from_self = False

        self.logger = logger or logging.getLogger("diagnostics")
        self.errors: list[DiagnosticError] = []

        # Set to true in raise_if_errors, to prevent doubling of errors when context manager catches own exception.
        self._raised_from_self = False

        self._collector_context_token: Optional[Token[Optional[DiagnosticCollector]]] = None

    @property
    def collector(self) -> DiagnosticCollector:
        """
        Diagnostic collector collects it's own errors, does not propagate it to the context, which can be any other collector.
        """
        return self

    def raise_if_errors(self) -> None:
        """
        Raises DiagnosticException if there are any collected errors. Otherwise, does nothing.
        """
        if bool(self):
            self._raised_from_self = True
            self.logger.debug("Raising exception from %r: %s", self, self.errors)
            raise DiagnosticException(detail=copy(self.errors))

    def __bool__(self) -> bool:
        """
        Whether the exception contains any error, therefore should be raised.
        """
        return bool(self.errors)

    def __enter__(self) -> Self:
        """
        Start context manager. At end of context, DiagnosticException is automatically raised when there are any errors.
        """
        self._collector_context_token = self.__class__._collector_context.set(self)

        # DiagnosticCollector overwrites context without parent, as it catches all errors and does not
        # populate it to the upper context. It acts as a root context that raises the exception on exit,
        # which in turn can be catched by higher order collector to include its errors, which in turn
        # completes the locations with higher order collector's context.
        self._diagnostic_context_token = self.__class__._diagnostic_context.set(
            _DiagnosticContext(
                self=self,
                prefix=self._init_context.prefix,
                suffix=self._init_context.suffix,
            )
        )

        self.logger.debug("Entering diagnostic context %r", self.__class__._diagnostic_context.get())

        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Automatically raises DiagnosticException if there is any diagnostic to be presented.

        If __exit__ occured because of another DiagnosticException, append errors from it to this diagnostic
        (with optionally specified prefix) and re-raise new DiagnosticException with all collected errors.
        """
        # Include errors from inner exception.
        if isinstance(exc_val, DiagnosticException):
            if not self._raised_from_self:
                self.include(exc_val)

        super().__exit__(exc_type, exc_val, exc_tb)

        if self._collector_context_token:
            self.__class__._collector_context.reset(self._collector_context_token)

        # Do not raise DiagnosticException if other exception (other than DiagnosticException) was raised,
        # as we don't want to shadow internal exceptions from user even if there are some diagnostics.
        if exc_val is None or isinstance(exc_val, DiagnosticException):
            self.raise_if_errors()
