# Setlogging

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/setlogging.svg)](https://badge.fury.io/py/setlogging)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A flexible Python logging utility with JSON support and timezone awareness.

## Author
- **Name:** Jie Yan
- **Contact:** kiki3890528@gmail.com

## Features

- JSON and plain text log formats
- Log file rotation with size limits
- Console output options
- Timezone-aware logging
- Customizable formatting
- Type-safe configuration

## Installation

```bash
pip install setlogging
```

## Usage

```python
from setlogging import get_logger

# Basic logging
logger = get_logger()
logger.info("Basic log message")

# JSON logging with indentation
logger = get_logger(json_format=True, indent=2)
logger.info("Structured logging")

# Custom file and rotation
logger = get_logger(
    log_file="/tmp/app.log",
    max_size_mb=10,  # 10MB
    backup_count=5
)

# Disable console output
logger = get_logger(console_output=False)
logger.info("This will not be printed to the console")
```

## Project Structure

```
setlogging/
├── src/
│   └── setlogging/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   └── test_logger.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Configuration Options

| Option          | Type    | Default                        | Description                             |
|-----------------|---------|--------------------------------|-----------------------------------------|
| `log_level`     | int     | `DEBUG`                        | Logging level                           |
| `log_file`      | str     | `app.log` or `app_json.log`    | Log file path                           |
| `max_size_mb`   | int     | `25`                           | Max file size in MB before rotation     |
| `backup_count`  | int     | `7`                            | Number of backup files                  |
| `console_output`| bool    | `True`                         | Enable console logging                  |
| `log_format`    | str     | `None`                         | Custom log format string                |
| `date_format`   | str     | `None`                         | Custom date format string               |
| `json_format`   | bool    | `False`                        | Enable JSON formatting                  |
| `indent`        | int     | `None`                         | JSON indentation level                  |



