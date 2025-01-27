# akmi-utils

A utility package for various functionalities including converting TOML files to YAML format, logging, and OpenTelemetry integration.

## Prerequisites

- Python 3.12 or higher
- Poetry

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/akmi-utils.git
    cd akmi-utils
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

## Usage

### Converting TOML to YAML

To use the `convert_toml_to_yaml` function, follow these steps:

1. Import the function in your script:
    ```python
    from akmi_utils.convert_toml_yaml import convert_toml_to_yaml
    ```

2. Call the function with the input TOML file path and output YAML file path:
    ```python
    convert_toml_to_yaml('path/to/input.toml', 'path/to/output.yaml')
    ```

### Logging Requests

To log requests in a FastAPI application, use the `log_requests` middleware:

1. Import and add the middleware to your FastAPI app:
    ```python
    from akmi_utils.logging import log_requests

    app = FastAPI()
    app.middleware('http')(log_requests)
    ```

### OpenTelemetry Integration

To set up OpenTelemetry with FastAPI, use the `setting_otlp` function and `PrometheusMiddleware`:

1. Import and configure OpenTelemetry in your FastAPI app:
    ```python
    from akmi_utils.otel import setting_otlp, PrometheusMiddleware, metrics

    app = FastAPI()
    setting_otlp(app, app_name='your_app_name', endpoint='your_otlp_endpoint')
    app.add_middleware(PrometheusMiddleware, app_name='your_app_name')
    app.add_route('/metrics', metrics)
    ```

## Running Tests

To run the tests, use the following command:
```sh
poetry run pytest