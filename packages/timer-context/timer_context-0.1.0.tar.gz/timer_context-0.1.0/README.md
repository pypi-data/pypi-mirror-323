# TimerContext
Context Manager for timing blocks of python code simply.

## Installation

Install TimerContext using pip, uv, or another package manager by downloading from PyPI.

```bash
pip install timer-context
```

```bash
uv pip install timer-context
```

## Usage

`TimerContext` is a context manager, and will time code used within a `with` block.

```python
import time


def func(x):
    time.sleep(x)

with TimerContext() as timer:
    func(3)
    timer.duration  # duration will be approximately 3 seconds
    func(2)
    timer.duration  # duration will be approximately 5 seconds
    func(1)
    timer.duration  # duration will be approximately 6 seconds

print(timer.start)
print(timer.end)
print(timer.duration)  # duration will be approximately 6 seconds
```

Any code inside of the context manager will contribute to the duration. As soon as the context is left, the timer will stop counting.

## API Reference

`TimerContext` has four attributes intended to be used by the user, `start`, `end`, `duration`, and `duration_ns`.

- `start` is simply a `datetime.datetime` object representing (approximately) when the context started.
- `end` is simply a `datetime.datetime` object representing (approximately) when the context ended.
- `duration` is a property representing the number of milliseconds of the duration of the timer (as a float). If the context is still ongoing, it will report the number of milliseconds since the timer context until duration was called. If the context is closed, then it will report the number of milliseconds the context was open.
- `duration_ns` is a property representing the number of nanoseconds of the duration of the timer (as an int).

## Notice on Resolution

The duration is always calculated using `time.perf_counter_ns` and then converted to milliseconds as a float. The precision of this timer is limited by the resolution of the performance counter on your particular environment.

The precision is also limited by the overhead of calling a context manager. If your context is exceptionally fast (on the order of single nanoseconds), this overhead is non-negligible, and you would be better served by calling `time.perf_counter_ns` directly. For any block that runs for longer than that, the overhead is proportionally small/negligible.

Because the counter used for duration is set after defining `timer.start` and before defining `timer.end`, `timer.duration` might not exactly equal `timer.end-timer.start`, generally. The times used for `start` and `end` are lower resolution than the performance counter for the duration. Thus, they should generally only be used for reference, and not for calculating a duration.

## Comparison with `timeit` and `cProfile`.

Timing/profiling Python code is generally done with the [`timeit`](https://docs.python.org/3/library/timeit.html) and/or [`cProfile](https://docs.python.org/3/library/profile.html) modules in the standard library. These are both great tools, and may be better suited for your task.

You should use `timeit` if:
- You need statistics on runtime by running an identical code snippet many times.

You should use `cProfile` if:
- You need more detailed reports on the runtime of individual lines/function calls. ([`cProfile.Profile`](https://docs.python.org/3/library/profile.html#profile.Profile) can also conveniently be used as a context manager!)

You should use `TimerContext` if:
- You need to only time a block of code once without interrupting its flow.
- You do not need detailed profiling reports
- Rewriting your block of code as a function would be inconvenient.
- You want an incredibly simple interface for timing code.

## Contributing

Please open an Issue if you find a bug or would like to request a feature. Bugs are generally fixed promptly. Because of `ContextTimer`'s goal of being a radically simple interface, complex feature requests will likely be closed, but genuine improvements that do not sacrifice the vision of simplicity may be considered. We recommend opening an issue to discuss new features before opening a Pull Request. Pull Requests for bug fixes are always welcome.
