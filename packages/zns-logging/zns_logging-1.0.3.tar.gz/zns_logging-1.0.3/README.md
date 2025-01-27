<h1 style="text-align: center">pypi_zns_logging</h1>

<hr style="width: 90%; margin: auto">

<h3 style="text-align: center">A simple and flexible logging library for Python</h3>

# Installation

```bash
pip install pypi-zns-logging
```

# Usage

```python
from zns_logging import get_logger

logger = get_logger(__name__, logging_level="DEBUG")

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

# Output

```
[2025-01-26 23:22:06] [DEBUG   ] [__main__]: This is a debug message
[2025-01-26 23:22:06] [INFO    ] [__main__]: This is an info message
[2025-01-26 23:22:06] [WARNING ] [__main__]: This is a warning message
[2025-01-26 23:22:06] [ERROR   ] [__main__]: This is an error message
[2025-01-26 23:22:06] [CRITICAL] [__main__]: This is a critical message
```
