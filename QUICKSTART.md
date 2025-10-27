# Quick Start Guide

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Running the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8080

# Or using make
make run
```

## Testing the API

### Valid XML
```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<root><item>value</item></root>'
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

### Invalid XML
```bash
curl -X POST http://localhost:8080/v5.0/validate \
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

## Running Tests

```bash
# Run all tests with coverage
pytest --cov=app -v

# Or using make
make test
```

## Code Quality

```bash
# Run all checks
make check

# Format code
make format

# Run linter
make lint
```

## Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Interactive Documentation

Once running, visit:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- Health Check: http://localhost:8080/healthz

## Key Features

✅ Secure XML parsing with defusedxml (XXE protection)  
✅ Rate limiting (60 req/min per IP by default)  
✅ Request body size limits (512KB default)  
✅ Timeout protection (2 seconds default)  
✅ JSON-formatted structured logging  
✅ Request ID correlation  
✅ 92.58% test coverage  
✅ Type-safe with mypy  
✅ Formatted with black  
✅ Linted with ruff  

## Next Steps

- See [README.md](README.md) for full documentation
- Check [app/validators/](app/validators/) to add custom validators
- Adjust settings in `.env` file (copy from `.env.example`)

