# TBint Logger Python

The TBINT Logger Python is a simple logger that
can also send logs to Datadog.

It streamlines the process of logging,
conforming to our standards.

## Usage

Create a .env file with the following content:

```sh
# LOG_LEVEL can be debug, info, warning, error
LOG_LEVEL=debug
DD_SERVICE_NAME=YOUR_SERVICE_NAME_HERE
DD_SOURCE=production_or_any_other_environment
# Get these values from Datadog
DD_API_ENDPOINT=https://http-intake.logs.datadoghq.eu/api/v2/logs
# Get these values from Datadog
DD_APP_KEY=YOUR_DD_APP_KEY
```

Create this python file:

```python
from tbint_logger import tbint_logger

logger = tbint_logger.Logger()

logger.info_sync(
    tbint_logger.Data(
        description="This is a test",
    )
)
```

## Development

```sh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*
```

