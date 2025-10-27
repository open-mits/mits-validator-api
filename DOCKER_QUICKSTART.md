# Docker Quick Start

Super simple! Just run:

```bash
docker-compose up -d
```

That's it! The service will be running on http://localhost:8080

## Test It

```bash
# Health check
curl http://localhost:8080/healthz

# Valid XML
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<root><item>value</item></root>'

# Invalid XML
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/json" \
  -d '{"xml":"<root><unclosed>"}'
```

## Interactive Docs

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Optional: Custom Configuration

Want to change settings? Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

Then uncomment the `env_file` section in `docker-compose.yml`.

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild after changes
docker-compose up -d --build
```

## What's Running?

- FastAPI application with 4 uvicorn workers
- Non-root user for security
- Health checks enabled
- Rate limiting: 60 requests/minute per IP
- Body size limit: 512KB
- All security features enabled (XXE protection, etc.)

See [README.md](README.md) for full documentation.

