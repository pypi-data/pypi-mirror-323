from __future__ import annotations
import time
import datetime
from typing import Any


class TimerContext:
    """Context manager to time a block of code using a `with` statement.

    Attributes:
        start: The start time.
        start_counter: A performance counter representing when the context
            began, in nanoseconds. This should only ever be compared against
            another performance counter.
        end: The end time (if the context manager has exited).
        end_counter: A performance counter representing when the context
            exited, in nanoseconds. This should only ever be compared against
            another performance counter.
        duration: The duration of the block of code. If the context manager has
            not exited, this will be the duration up to the current time.

    Note:
        Because of the additional overhead of the context manager, this may not
        be the most accurate way to time a block of fast code, in the order of
        single nanoseconds. For a slow block of code, the overhead should be
        proportionally small.

    Examples:
        >>> import time
        >>> with TimerContext() as operation_timer:
        ...     print(operation_timer.start)
        ...     print(operation_timer.duration)
        ...     print(time.sleep(2))
        ...     print(operation_timer.duration)
        ... print(operation_timer.end)
        ... print(operation_timer.duration)
        ... time.sleep(2)
        ... print(operation_timer.duration)

    """

    start: datetime.datetime
    start_counter: int
    end: datetime.datetime | None
    end_counter: int | None

    def __enter__(self) -> TimerContext:
        self.end = None
        self.end_counter = None
        # Start the counter last because datetime.datetime.now() takes longer
        # than the perf_counter, and the counter needs to be more precise.
        self.start = datetime.datetime.now()
        self.start_counter = time.perf_counter_ns()
        return self

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        # End the counter first because datetime.datetime.now() takes longer
        # than the perf_counter, and the counter needs to be more precise.
        self.end_counter = time.perf_counter_ns()
        self.end = datetime.datetime.now()

    @property
    def duration_ns(self) -> int:
        """The duration of the block of code, in nanoseconds."""
        return (self.end_counter or time.perf_counter_ns()) - self.start_counter

    @property
    def duration(self) -> float:
        """The duration of the block of code, in milliseconds."""
        return self.duration_ns / 1e6
