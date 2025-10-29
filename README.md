# mits-validator-api

Production-grade FastAPI service for validating **MITS 5.0 (Rental Options & Fees)** XML documents.

Implements all **110 validation rules** defined in the MITS 5.0 specification, organized into 20 logical sections (A-T).

## Features

### Core Validation
- **Comprehensive MITS 5.0 Validation**: All 110 rules across sections A-T
- **Structured Error Reporting**: Clear, actionable messages with rule IDs and element paths
- **Well-formedness & Encoding**: UTF-8 validation, entity protection
- **Class & Item Structure**: ChargeOfferClass, ChargeOfferItem validation
- **Amount Semantics**: Explicit, Percentage Of, Stepped, Variable, Included
- **Specialized Items**: Pet, Parking, Storage offer validation
- **Cross-validation**: Reference integrity, circular dependency detection
- **Duplicate Detection**: Name uniqueness, exact duplicate identification

### Security & Performance
- **Secure XML Parsing**: defusedxml with XXE and entity expansion protection
- **Rate Limiting**: 60 requests/minute per IP (configurable)
- **Body Size Limits**: 512 KB max (configurable)
- **Timeout Protection**: 2-second validation timeout
- **Short-circuit Validation**: Fail fast on critical errors

### Developer Experience
- **FastAPI Framework**: Modern, async Python API
- **OpenAPI Documentation**: Interactive docs at `/docs`
- **Structured Logging**: JSON logs with request ID correlation
- **Health Checks**: `/healthz` endpoint
- **Docker Support**: One-command deployment
- **Comprehensive Tests**: >90% coverage with unit and integration tests

## Quick Start

### Using Docker (Recommended)

```bash
# Start the service
docker-compose up -d

# Validate a document
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @your_mits_file.xml
```

See [MITS_QUICKSTART.md](MITS_QUICKSTART.md) for detailed examples.

### Local Development

```bash
# Install dependencies
pip install -e .

# Run tests
make test

# Start development server
make serve
```

See [QUICKSTART.md](QUICKSTART.md) for complete setup instructions.

## API Examples

### Valid Document

**Request:**

```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="1">
        <ChargeOfferClass Code="APP">
            <ChargeOfferItem InternalCode="app_fee">
                <Name>Application Fee</Name>
                <Description>One-time application fee</Description>
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                    <Lifecycle>At Application</Lifecycle>
                    <PaymentFrequency>One-time</PaymentFrequency>
                </Characteristics>
                <AmountBasis>Explicit</AmountBasis>
                <ChargeOfferAmount>
                    <Amounts>50.00</Amounts>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>'
```

**Response:**

```json
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "info": []
}
```

### Invalid Document

**Request:**

```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="1">
        <ChargeOfferClass Code="APP">
            <ChargeOfferItem InternalCode="app_fee">
                <!-- Missing Name and Description -->
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                </Characteristics>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>'
```

**Response:**

```json
{
    "valid": false,
    "errors": [
        "[F.30] Item 'app_fee' in class 'APP' missing required <Name> element",
        "[F.31] Item 'app_fee' in class 'APP' missing required <Description> element",
        "[F.32] Item 'app_fee' in class 'APP' missing required <Characteristics> element",
        "[F.33] Item 'app_fee' in class 'APP' must contain at least one <ChargeOfferAmount> element"
    ],
    "warnings": [],
    "info": []
}
```

## Validation Rules

The validator implements **110 rules** organized into 20 sections:

| Section | Rules | Description |
|---------|-------|-------------|
| **A** | 1-6 | XML Container & Basics |
| **B** | 7-10 | Fee Placement Scope |
| **C** | 11-14 | Per-Level Identity Hygiene |
| **D** | 15-20 | ChargeOfferClass Structure |
| **E** | 21-26 | Class Limits |
| **F** | 27-41 | Offer Item Structure |
| **G** | 42-49 | Item Characteristics |
| **H** | 50-56 | Amount Basis |
| **I** | 57-65 | Amount Blocks |
| **J** | 66-69 | AmountPerType & Frequency |
| **K** | 70-74 | PetOfferItem |
| **L** | 75-78 | ParkingOfferItem |
| **M** | 79-81 | StorageOfferItem |
| **N** | 82-89 | Intra-class Integrity |
| **O** | 90-94 | Percentage-of References |
| **P** | 95-97 | Included Items |
| **Q** | 98-102 | Text & Whitespace Hygiene |
| **R** | 103-105 | Date/Time Consistency |
| **S** | 106-108 | Frequency vs Basis |
| **T** | 109-110 | Duplicates & Collisions |

See [MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md) for complete rule documentation.

## Architecture

```
app/
├── validators/
│   ├── mits/                    # MITS 5.0 validators (110 rules)
│   │   ├── __init__.py
│   │   ├── base.py              # Base classes, ValidationResult
│   │   ├── enums.py             # Enumeration definitions
│   │   ├── orchestrator.py      # Main coordinator
│   │   ├── section_a_xml_basics.py      # Rules 1-6
│   │   ├── section_b_fee_placement.py   # Rules 7-10
│   │   ├── section_c_identity.py        # Rules 11-14
│   │   ├── section_d_class_structure.py # Rules 15-20
│   │   ├── section_e_class_limits.py    # Rules 21-26
│   │   ├── section_f_offer_items.py     # Rules 27-41
│   │   ├── section_g_characteristics.py # Rules 42-49
│   │   ├── section_h_amount_basis.py    # Rules 50-56
│   │   ├── section_i_amount_blocks.py   # Rules 57-65
│   │   ├── section_j_frequency.py       # Rules 66-69
│   │   ├── section_k_pet_items.py       # Rules 70-74
│   │   ├── section_l_parking_items.py   # Rules 75-78
│   │   ├── section_m_storage_items.py   # Rules 79-81
│   │   ├── section_n_o_p_integrity.py   # Rules 82-97
│   │   └── section_q_r_s_t_final.py     # Rules 98-110
│   └── xml_basic.py            # Basic XML validation
├── api/
│   └── v5.py                   # POST /v5.0/validate endpoint
├── services/
│   └── validation_service.py   # Orchestration layer
├── models/
│   └── dto.py                  # Request/Response models
├── config.py                   # Settings management
├── middleware.py               # Request ID, logging, body limits
├── security.py                 # Rate limiting, input sanitization
└── main.py                     # FastAPI application
```

## Testing

```bash
# Run all tests
make test

# MITS validator tests only
pytest tests/validators/mits/ -v

# With coverage
pytest --cov=app --cov-report=html

# Test with official files
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_full.xml
```

Test files included:
- `tests/test_full.xml`: Complete MITS 5.0 document (13,868 lines)
- `tests/test_partial.xml`: Partial document for specific scenarios

## Configuration

Environment variables (`.env` or `docker-compose.yml`):

```bash
# Service
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_DOCS=true

# Security
MAX_BODY_BYTES=524288          # 512 KB max request size
RATE_LIMIT=60/minute           # Rate limiting
REQUEST_TIMEOUT_SECONDS=2      # Validation timeout

# CORS
ALLOWED_ORIGINS=               # Comma-separated origins (empty = disabled)
ALLOW_CREDENTIALS=false
ALLOWED_METHODS=POST
ALLOWED_HEADERS=*
```

## API Endpoints

### `POST /v5.0/validate`

Validates MITS 5.0 XML documents.

**Headers:**
- `Content-Type`: `application/xml` or `text/xml`

**Body:** Raw XML document

**Response:** Always `200 OK` with validation results

```json
{
    "valid": boolean,
    "errors": ["Rule-based error messages with [RULE_ID]"],
    "warnings": ["Warning messages"],
    "info": ["Informational messages"]
}
```

**Error Scenarios (4xx/5xx):**
- `413 Request Entity Too Large`: Body exceeds MAX_BODY_BYTES
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Unexpected server error

### `GET /healthz`

Health check endpoint.

**Response:** `200 OK`

```json
{
    "status": "healthy"
}
```

### `GET /docs`

Interactive OpenAPI documentation (if `ENABLE_DOCS=true`).

## Security

### XXE Protection

Uses `defusedxml` with:
- External entity expansion disabled
- DTD processing disabled
- Entity reference limits enforced

### Rate Limiting

IP-based token bucket (configurable):
- Default: 60 requests/minute per IP
- Returns `429 Too Many Requests` when exceeded

### Input Sanitization

- BOM stripping
- Control character validation
- Length checks before processing
- UTF-8 encoding enforcement

### Timeouts

- 2-second timeout for validation operations
- Prevents CPU exhaustion on malformed documents

## Documentation

- **[MITS_QUICKSTART.md](MITS_QUICKSTART.md)**: Quick start guide with examples
- **[MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md)**: Complete validation rule reference
- **[QUICKSTART.md](QUICKSTART.md)**: Local development setup
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)**: Docker deployment guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Technical architecture details

## Development

### Running Locally

```bash
# Install dependencies
pip install -e .

# Run linters
make lint

# Format code
make format

# Type check
make typecheck

# Run tests
make test

# Start dev server
make serve
```

### Adding Custom Validators

See [MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md) for instructions on:
- Adding new validation rules
- Creating custom sections
- Extending existing validators

### Code Quality

- **Linting**: ruff
- **Formatting**: black
- **Type Checking**: mypy
- **Testing**: pytest with >90% coverage
- **CI/CD**: GitHub Actions

## License

MIT License - see [LICENSE](LICENSE) file.

## Resources

- **MITS 5.0 Specification**: https://www.naa.org/mits
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **defusedxml**: https://github.com/tiran/defusedxml

---

**Built with ❤️ for the multifamily industry**
