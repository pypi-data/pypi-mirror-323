import time
from timer_context import TimerContext
from hypothesis import strategies as st
import hypothesis
import pytest

# Define a common strategy for sleep times
sleep_time_strategy = st.floats(min_value=1e-9, max_value=1e-2)


def greater_or_approximately_equal(value: float, target: float, rel: float = 0.1) -> None:
    """Assert than value is greater than or approximately equal to target."""
    assert value > target or pytest.approx(target, rel) == value


def test_initialization() -> None:
    """Test that TimerContext initializes correctly, setting start time and performance counter."""
    with TimerContext() as timer:
        assert timer.start is not None
        assert timer.end is None
        assert timer.start_counter > 0


@hypothesis.given(sleep_time=sleep_time_strategy)
def test_duration_calculation(sleep_time: float) -> None:
    """Test that TimerContext calculates the duration correctly for a given block of code."""
    with TimerContext() as timer:
        time.sleep(sleep_time)
        incomplete_duration = timer.duration
        greater_or_approximately_equal(incomplete_duration, sleep_time * 1000)
        time.sleep(sleep_time)

    complete_duration = timer.duration
    assert incomplete_duration != complete_duration
    greater_or_approximately_equal(complete_duration, sleep_time * 2 / 1000)


def test_end_values() -> None:
    """Test that TimerContext sets end values correctly after exiting the context and the duration remains constant."""
    with TimerContext() as timer:
        time.sleep(0.1)
    duration_after_exit = timer.duration
    assert timer.end is not None
    assert timer.end_counter is not None
    assert duration_after_exit > 0
    # Ensure duration does not change after the context has ended
    assert duration_after_exit == timer.duration


@hypothesis.given(sleep_time_outer=sleep_time_strategy, sleep_time_inner=sleep_time_strategy)
def test_nested_contexts(sleep_time_outer: float, sleep_time_inner: float) -> None:
    """Test that nested TimerContext instances work correctly and track independent durations."""
    with TimerContext() as outer_timer:
        time.sleep(sleep_time_outer)
        with TimerContext() as inner_timer:
            time.sleep(sleep_time_inner)
        greater_or_approximately_equal(inner_timer.duration, sleep_time_inner * 1000)
    greater_or_approximately_equal(outer_timer.duration, (sleep_time_outer + sleep_time_inner) * 1000)


@hypothesis.given(sleep_time=sleep_time_strategy)
def test_duration_consistency(sleep_time: float) -> None:
    """Test that duration in milliseconds is consistent with duration in nanoseconds."""
    with TimerContext() as timer:
        time.sleep(sleep_time)
    assert pytest.approx(timer.duration) == timer.duration_ns / 1e6


@hypothesis.given(sleep_time=sleep_time_strategy)
def test_exception_handling(sleep_time: float) -> None:
    """Test that TimerContext tracks time correctly even if an exception is raised in the block."""
    try:
        with TimerContext() as timer:
            time.sleep(sleep_time)
            raise ValueError("Intentional error")
    except ValueError:
        pass
    assert timer.end is not None
    greater_or_approximately_equal(timer.duration, sleep_time * 1000)
