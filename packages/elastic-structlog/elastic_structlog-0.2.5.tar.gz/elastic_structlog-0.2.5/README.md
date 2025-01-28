# Elastic Structlog Extension - 'elastic_structlog'

elastic_structlog is python package that provides functionality in order to send logs to elastic directly.
This package is an extension for the package 'structlog'. In order to use the library suggesting to read the [official documentation of structlog](https://www.structlog.org/en/stable/getting-started.html#installation)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install elastic_structlog.

```bash
pip install elastic_structlog
```

## Usage
### Configuration:
In order to configure the logger, the package provide two options:

#### Manual Confuguration:

```python
from elastic_structlog import ESStructLogExtension, ESStructLogProcessor
import structlog
# First create ESStructLogExtension instance.
es_extension = ESStructLogExtension(
    host="https://HOST:PORT",
    basic_auth=("USER_NAME", "PASSWORD"),
    index="INDEX_EXAMPLE",
    flush_frequency=5,
    raise_on_indexing_error=False,
    verify_certs=True
)

# Second, configure the structlog - use directly the original module of structlog.
# Notice how you should use the processor that the package offers:
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        ESStructLogProcessor(es_extension=es_extension),
        structlog.processors.KeyValueRenderer()
    ]
)
```

#### Built-in 'configure_es_structlog_logger' function:
```python
from elastic_structlog.elastic_processor import configure_es_structlog_logger

configure_es_structlog_logger(
    host="https://HOST:PORT",
    basic_auth=("USER_NAME", "PASSWORD"),
    index="INDEX_EXAMPLE",
    flush_frequency=5,
    verify_certs=False, #Default - True
    raise_on_indexing_error=True #Default - False
)
```

## SDI Team - Nuriel Gadilov - 1.20.2025