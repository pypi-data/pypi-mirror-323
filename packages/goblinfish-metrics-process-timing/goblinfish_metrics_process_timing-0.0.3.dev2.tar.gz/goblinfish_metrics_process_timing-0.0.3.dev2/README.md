# The goblinfish.metrics.process_timing Package

> Provides context-manager classes to name, track and report elapsed-time and other metrics for top-level process entry-points (like AWS Lambda Function handlers) and sub-processes within them.

## Quick Start

Install in your project:

```shell
# Install with pip
pip install goblinfish-metrics-process_timing
```

```shell
# Install with pipenv
pipenv install goblinfish-metrics-process_timing
```

Import in your code:

```python
from goblinfish.metrics.process_timing import ProcessTimer
```

Create the timing-tracker instance:

```python
tracker = ProcessTimer()
```

Decorate your top-level/entry-point function:

```python
@tracker.track
def some_function():
    ...
```

Add any sub-process timers:

```python
@tracker.track
def some_function():
    ...

    with tracker.timer('some_process_name'):
        # Do stuff here
        ...
```

When this code is executed, after the context created by the `@tracker.track` decorator is complete, it will `print` something that looks like this:

```json
{"some_process_name": 0.0, "some_function": 0.0}
```

More detailed examples can be found in [the `examples` directory](https://bitbucket.org/stonefish-software-studio/stonefish-metrics-process_timer-package/src/main/examples/) in the repository.

## Contribution guidelines

At this point, contributions are not accepted — I need to finish configuring the repository, deciding on whether I want to set up automated builds for pull-requests, and probably several other items.

## Who do I talk to?

The current maintainer(s) will always be listed in the `[maintainers]` section of [the `pyproject.toml` file](https://bitbucket.org/stonefish-software-studio/stonefish-metrics-process_timer-package/src/main/pyproject.toml) in the repository.
