# glampy

This project intends to allow building useful, reliable and beautiful python CLIs with ease.

## Installation

Stable release version:

```bash
pip install glampy
```

Latest development version:

```bash
pip install git+https://github.com/snaeil/glampy
```

## Usage

### Logging

The customized logger can be used in it's default optionated way or can be customized.  
It is fully compatible with the standard python logging module.

```python
from glampy.logging import Logger

# Example using the Logger class to log to stdout and a file:
logger = Logger("my_logger", log_file="my_log.log", log_level=logging.DEBUG)
logger.debug("This is a debug message that will be logged to stdout and the file.")

# Example using the Logger class to log to a file only:
logger = Logger("my_logger", console_handler=None, log_level=logging.DEBUG)
logger.debug("This is a debug message that will be logged to a file only.")

# Example using the Logger class to log to stdout only:
logger = Logger("my_logger", log_level=logging.WARNING)
logger.warning("This is a warning message that will be logged to stdout only.")
logger.info("This is an info message that will not be logged.")
```

### Style

The style module provides a simple way to style text in the terminal.  
See [the source code](https://github.com/snaeil/glampy/blob/main/glampy/style.py) for all available styles.

```python
from glampy.style import Style, Sign, Foreground_Colour, Background_Colour

# Example using the Style class to style text:
print(f"{Sign.WARNING} The word {Style.bold}bold{Style.RESET_ALL} is not {style.italic}italic{Style.RESET_ALL}.")
```

## Contributing

Contributions are welcome!
For feature requests, bug reports or questions, please open an issue.
For code contributions, please open a pull request.

Please make sure to install `pre-commit` before making changes to the code (this enables
checks for code formatting, linting, etc. before committing changes):

```bash
pip install poetry
poetry install
cd path/to/glampy
pre-commit install
```
