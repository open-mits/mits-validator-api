# MITS Validator API

[![CI](https://github.com/your-org/mits-validator-api/workflows/CI/badge.svg)](https://github.com/your-org/mits-validator-api/actions)
[![codecov](https://codecov.io/gh/your-org/mits-validator-api/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/mits-validator-api)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-grade FastAPI service for validating MTS5 (RETTC) XML payloads. Built with security, performance, and extensibility in mind.

## Features

- ✅ **Secure XML Parsing**: Uses `defusedxml` to protect against XXE, entity expansion, and other XML-based attacks
- 🚀 **High Performance**: Async FastAPI with configurable worker processes
- 🔒 **Rate Limiting**: IP-based rate limiting to prevent abuse
- 📊 **Comprehensive Logging**: JSON-formatted structured logging with request ID correlation
- 🧪 **Well Tested**: >90% test coverage with unit and property-based tests
- 🔧 **Production Ready**: Docker support, health checks, graceful shutdown
- 📚 **Interactive Docs**: Auto-generated OpenAPI/Swagger documentation
- 🎯 **Extensible**: Easy-to-extend validator architecture for adding custom validation rules

## Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Security](#security)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-org/mits-validator-api.git
cd mits-validator-api
```

2. **Install dependencies**:
```bash
# Using pip
pip install -e ".[dev]"

# Or using make
make dev-install
```

3. **Configure environment** (optional):
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

4. **Run the application**:
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8080

# Or using make
make run
```

5. **Access the API**:
- API: http://localhost:8080
- Interactive docs: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- Health check: http://localhost:8080/healthz

### Docker Quick Start

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use Makefile
make docker-build
make docker-run

# View logs
make docker-logs

# Stop
make docker-stop
```

## API Documentation

### Endpoint: `POST /v5.0/validate`

Validates MTS5 (RETTC) XML payloads for well-formedness and compliance.

#### Request Formats

**Option 1: Raw XML Body**

```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<root><item>value</item></root>'
```

**Option 2: JSON-Wrapped XML**

```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/json" \
  -d '{"xml": "<root><item>value</item></root>"}'
```

#### Response Format

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "info": []
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| 200  | Request processed successfully (check `valid` field for result) |
| 400  | Malformed request (invalid content type, empty body, etc.) |
| 413  | Request body too large (exceeds configured limit) |
| 422  | Validation error in request format |
| 429  | Rate limit exceeded |
| 500  | Internal server error |

#### Examples

**Valid XML**:
```bash
curl -s -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<?xml version="1.0"?>
<root>
  <header>
    <timestamp>2025-10-27T10:00:00Z</timestamp>
  </header>
  <body>
    <item id="1">
      <name>Test</name>
    </item>
  </body>
</root>'
```

Response:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "info": []
}
```

**Invalid XML**:
```bash
curl -s -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/json" \
  -d '{"xml": "<root><unclosed>"}'
```

Response:
```json
{
  "valid": false,
  "errors": ["Invalid XML"],
  "warnings": [],
  "info": []
}
```

### Health Check Endpoint

```bash
curl http://localhost:8080/healthz
```

Response:
```json
{
  "status": "healthy",
  "service": "mits-validator-api",
  "version": "0.1.0"
}
```

## Architecture

### High-Level Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│  ┌───────────────────────────────────────────┐  │
│  │         Middleware Stack                  │  │
│  │  • Request ID Generation                  │  │
│  │  • Body Size Limiting                     │  │
│  │  • JSON Logging                           │  │
│  │  • Rate Limiting (slowapi)                │  │
│  └───────────────────────────────────────────┘  │
│                     ↓                            │
│  ┌───────────────────────────────────────────┐  │
│  │      API Router (v5.0/validate)           │  │
│  │  • Content-Type validation                │  │
│  │  • Request body parsing                   │  │
│  │  • Timeout protection                     │  │
│  └───────────────────────────────────────────┘  │
│                     ↓                            │
│  ┌───────────────────────────────────────────┐  │
│  │       Validation Service Layer            │  │
│  │  • Input sanitization                     │  │
│  │  • Validator orchestration                │  │
│  │  • Result aggregation                     │  │
│  └───────────────────────────────────────────┘  │
│                     ↓                            │
│  ┌───────────────────────────────────────────┐  │
│  │           Validator Modules               │  │
│  │  • xml_basic: Well-formedness check       │  │
│  │  • [Future]: Schema validation            │  │
│  │  • [Future]: Business rule validation     │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                     ↓
              ┌──────────────┐
              │  defusedxml  │
              │  (Safe Parse)│
              └──────────────┘
```

### Directory Structure

```
mits-validator-api/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Settings (pydantic-settings)
│   ├── middleware.py             # Custom middleware
│   ├── errors.py                 # Exception handlers
│   ├── security.py               # Rate limiting & sanitization
│   ├── api/
│   │   ├── __init__.py
│   │   └── v5.py                 # Validation endpoint
│   ├── models/
│   │   ├── __init__.py
│   │   └── dto.py                # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── validation_service.py # Orchestration layer
│   └── validators/
│       ├── __init__.py
│       └── xml_basic.py          # Well-formedness validator
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_api_validate.py     # API tests
│   ├── test_xml_basic.py        # Validator tests
│   └── test_validation_service.py
├── .github/workflows/
│   └── ci.yml                    # CI/CD pipeline
├── pyproject.toml                # Project metadata & dependencies
├── Dockerfile                    # Production container
├── docker-compose.yml            # Local development
├── Makefile                      # Development commands
├── pytest.ini                    # Test configuration
└── README.md
```

## Security

### XML Attack Prevention

This service uses `defusedxml` to protect against common XML-based attacks:

| Attack Type | Protection Method |
|-------------|-------------------|
| **XXE (XML External Entity)** | External entity expansion disabled |
| **Billion Laughs** | Entity expansion limits enforced |
| **DTD Retrieval** | DTD processing disabled |
| **Quadratic Blowup** | Parser configured with safe defaults |

### Rate Limiting

- **Default**: 60 requests per minute per IP address
- **Configurable**: Via `RATE_LIMIT` environment variable
- **Strategy**: Token bucket algorithm using `slowapi`
- **Bypass**: Rate limiting can be disabled in testing environments

### Input Validation

- **Body Size Limit**: 512 KB default (configurable)
- **Character Validation**: Rejects illegal XML 1.0 control characters
- **BOM Stripping**: Automatically removes UTF-8 BOM
- **Timeout Protection**: 2-second default timeout for parsing operations

### Best Practices

1. **Always use HTTPS** in production to encrypt data in transit
2. **Configure CORS** appropriately via `ALLOWED_ORIGINS`
3. **Monitor rate limits** and adjust based on legitimate traffic patterns
4. **Review logs** regularly for suspicious patterns
5. **Keep dependencies updated** to patch security vulnerabilities

## Configuration

Configuration is managed via environment variables. See `.env.example` for all available options.

### Key Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_BODY_BYTES` | 524288 (512 KB) | Maximum request body size |
| `RATE_LIMIT` | "60/minute" | Rate limit per IP |
| `REQUEST_TIMEOUT_SECONDS` | 2 | XML parsing timeout |
| `MAX_XML_DEPTH` | 100 | Maximum XML nesting depth |
| `LOG_LEVEL` | INFO | Logging verbosity |
| `ENABLE_DOCS` | true | Enable OpenAPI docs |
| `ALLOWED_ORIGINS` | [] | CORS allowed origins |

### Environment Files

```bash
# Development
cp .env.example .env
# Edit .env for local settings

# Production
# Set environment variables in your deployment platform
# Do NOT commit .env files to version control
```

## Development

### Setup

```bash
# Install with dev dependencies
make dev-install

# Or manually
pip install -e ".[dev]"
```

### Running Locally

```bash
# Development server with auto-reload
make run

# Production mode
make serve
```

### Code Quality

```bash
# Run all checks
make check

# Individual checks
make lint          # Run ruff linter
make format-check  # Check code formatting
make typecheck     # Run mypy type checker

# Auto-fix issues
make fix           # Auto-fix lint and format issues
```

### Adding New Validators

To add a new validation rule:

1. **Create validator module**: `app/validators/my_validator.py`

```python
def validate_my_rule(xml_text: str) -> bool:
    """
    Validate custom rule.
    
    Args:
        xml_text: XML content as string
    
    Returns:
        True if valid, False otherwise
    """
    # Your validation logic here
    return True
```

2. **Register in service**: Edit `app/services/validation_service.py`

```python
from app.validators.my_validator import validate_my_rule

def validate(xml_text: str) -> Dict[str, List[str] | bool]:
    # ... existing code ...
    
    # Add your validator
    if not validate_my_rule(sanitized_xml):
        errors.append("Custom validation failed")
    
    # ... rest of code ...
```

3. **Add tests**: Create `tests/test_my_validator.py`

4. **Update documentation**: Add details to this README

## Testing

### Running Tests

```bash
# Run all tests with coverage
make test

# Fast run (no coverage)
make test-fast

# Verbose output
make test-verbose

# Run specific test file
pytest tests/test_xml_basic.py -v

# Run specific test
pytest tests/test_api_validate.py::TestValidationEndpoint::test_validate_raw_xml_valid -v
```

### Coverage Requirements

- **Minimum**: 90% code coverage (enforced in CI)
- **Reports**: Generated in `htmlcov/` directory
- **View coverage**: Open `htmlcov/index.html` in browser

### Test Categories

- **Unit Tests**: Individual component tests
- **Integration Tests**: End-to-end API tests
- **Property Tests**: Hypothesis-based fuzzing tests
- **Security Tests**: XXE and attack vector tests

## Deployment

### Docker Deployment

**Build image**:
```bash
docker build -t mits-validator-api:latest .
```

**Run container**:
```bash
docker run -d \
  -p 8080:8080 \
  -e MAX_BODY_BYTES=524288 \
  -e RATE_LIMIT="100/minute" \
  --name mits-validator \
  mits-validator-api:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mits-validator-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mits-validator-api
  template:
    metadata:
      labels:
        app: mits-validator-api
    spec:
      containers:
      - name: api
        image: mits-validator-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mits-validator-api
spec:
  selector:
    app: mits-validator-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure appropriate `RATE_LIMIT`
- [ ] Set up HTTPS/TLS termination
- [ ] Configure `ALLOWED_ORIGINS` for CORS
- [ ] Set up log aggregation (e.g., ELK, Splunk)
- [ ] Configure monitoring and alerts
- [ ] Set resource limits (CPU/memory)
- [ ] Enable health checks
- [ ] Set up auto-scaling policies
- [ ] Review and adjust `MAX_BODY_BYTES`
- [ ] Disable `ENABLE_DOCS` in production (optional)

## CI/CD

### GitHub Actions

The project includes a comprehensive CI/CD pipeline that runs on every push and pull request:

1. **Linting**: Checks code style with `ruff` and `black`
2. **Type Checking**: Static analysis with `mypy`
3. **Testing**: Runs test suite on Python 3.11 and 3.12
4. **Security Scanning**: Analyzes code with `bandit` and checks for known vulnerabilities
5. **Build**: Creates Docker image and verifies build succeeds

### Local CI Simulation

```bash
# Run the same checks as CI
make ci
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** checks: `make check test`
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Code Standards

- **Style**: Follow PEP 8 (enforced by `black` and `ruff`)
- **Types**: Add type hints to all functions
- **Tests**: Maintain ≥90% coverage
- **Docs**: Update README for user-facing changes
- **Commits**: Write clear, descriptive commit messages

### Development Workflow

```bash
# 1. Setup
make dev-install

# 2. Make changes
# ... edit files ...

# 3. Test changes
make test

# 4. Check code quality
make check

# 5. Auto-fix issues
make fix

# 6. Verify everything passes
make ci
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/mits-validator-api/issues)
- **Documentation**: [API Docs](http://localhost:8080/docs) (when running locally)
- **Email**: your.email@example.com

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- XML security via [defusedxml](https://github.com/tiran/defusedxml)
- Rate limiting via [slowapi](https://github.com/laurents/slowapi)

---

**Made with ❤️ for secure XML validation**
