# LifecycleLogging

A comprehensive logging utility for managing application lifecycle logs, combining the power of Python's `logging` with rich output formatting.

## Installation

```bash
pip install lifecyclelogging
```

## Features

- Configurable console and file logging outputs
- Rich formatting for enhanced readability
- Message storage with context and storage markers
- Verbosity controls with bypass markers
- JSON data attachment support
- Type-safe implementation
- Seamless integration with existing logging systems
- Automatic Gunicorn logger integration

## Basic Usage

```python
from lifecyclelogging import Logging

# Initialize logger
logger = Logging(
    enable_console=True,  # Enable console output
    enable_file=True,     # Enable file output
    logger_name="my_app"
)

# Basic logging
logger.logged_statement("Basic message", log_level="info")

# With context marker
logger.logged_statement(
    "Message with context",
    context_marker="STARTUP",
    log_level="info"
)

# With JSON data
logger.logged_statement(
    "Message with data",
    json_data={"key": "value"},
    log_level="debug"
)
```

## Advanced Features

### Verbosity Control

```python
logger = Logging(
    enable_verbose_output=True,
    verbosity_threshold=2
)

# Only logged if verbosity threshold allows
logger.logged_statement(
    "Detailed debug info",
    verbose=True,
    verbosity=2,
    log_level="debug"
)
```

### Message Storage

```python
# Store message under a marker
logger.logged_statement(
    "Important event",
    storage_marker="EVENTS",
    log_level="info"
)

# Access stored messages
events = logger.stored_messages["EVENTS"]
```

### Gunicorn Integration

When running under Gunicorn, LifecycleLogging automatically detects and inherits Gunicorn's logger configuration:

```python
# The logger will automatically use Gunicorn's handlers if available
logger = Logging(
    enable_console=True,
    enable_file=True
)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev,test,docs]"

# Run tests
make test

# Run linting and type checks
make check

# Build documentation
make docs
```

## Documentation

Full documentation is available in the [docs](docs/) directory.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Happy Logging!**
