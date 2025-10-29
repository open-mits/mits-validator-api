# MITS 5.0 Validator Quick Start

## What is this?

The **MITS 5.0 Validator** is a comprehensive validation service for MITS (Multifamily Information and Transaction Standard) 5.0 XML documents, specifically for rental options and fees.

It implements **all 110 validation rules** defined in the MITS 5.0 specification, organized into 20 logical sections (A-T).

## Quick Test

### 1. Start the Service

```bash
docker-compose up -d
```

### 2. Validate a Document

**Valid Document:**

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
                    <Percentage></Percentage>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>' | python3 -m json.tool
```

Expected response:

```json
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "info": []
}
```

**Invalid Document (Missing Required Fields):**

```bash
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data '<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="1">
        <ChargeOfferClass Code="APP">
            <ChargeOfferItem InternalCode="app_fee">
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                    <Lifecycle>At Application</Lifecycle>
                </Characteristics>
                <ChargeOfferAmount>
                    <Amounts>50.00</Amounts>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>' | python3 -m json.tool
```

Expected response (with errors):

```json
{
    "valid": false,
    "errors": [
        "[F.30] Item 'app_fee' in class 'APP' missing required <Name> element",
        "[F.31] Item 'app_fee' in class 'APP' missing required <Description> element"
    ],
    "warnings": [],
    "info": []
}
```

### 3. Test with Official Files

Use the included official MITS 5.0 test files:

```bash
# Full MITS 5.0 document
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_full.xml | python3 -m json.tool

# Partial document
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_partial.xml | python3 -m json.tool
```

## What Gets Validated?

The validator checks **110 rules** across these categories:

### ✅ Critical Structure (Sections A-C)
- XML well-formedness and encoding
- Root element and Property presence
- ID uniqueness across Building, Floorplan, ILS_Unit

### ✅ Class & Limits (Sections D-E)
- ChargeOfferClass structure and codes
- Class limits (MaximumOccurences, MaximumAmount)

### ✅ Items & Amounts (Sections F-I)
- Offer item structure (Name, Description, InternalCode)
- Characteristics (ChargeRequirement, Lifecycle, PaymentFrequency)
- Amount basis (Explicit, Percentage Of, Stepped, Variable, Included)
- Numeric formats and date validation

### ✅ Specialized Items (Sections J-M)
- AmountPerType and frequency alignment
- Pet, Parking, and Storage item specifics

### ✅ Cross-Validation (Sections N-P)
- Code uniqueness and integrity
- Percentage-of reference resolution
- Circular dependency detection
- Included item semantics

### ✅ Final Checks (Sections Q-T)
- Text hygiene and control characters
- Date consistency
- Frequency vs basis coherence
- Duplicate detection

## Common Validation Scenarios

### Scenario 1: Application Fee (Simple)

```xml
<ChargeOfferItem InternalCode="app_fee">
    <Name>Application Fee</Name>
    <Description>Non-refundable application processing fee</Description>
    <Characteristics>
        <ChargeRequirement>Mandatory</ChargeRequirement>
        <Lifecycle>At Application</Lifecycle>
        <PaymentFrequency>One-time</PaymentFrequency>
        <Refundability>Non-refundable</Refundability>
    </Characteristics>
    <AmountBasis>Explicit</AmountBasis>
    <AmountPerType>Applicant</AmountPerType>
    <ChargeOfferAmount>
        <Amounts>50.00</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
</ChargeOfferItem>
```

✅ **Valid**: Has all required fields, proper enumerations, and explicit amount.

### Scenario 2: Late Fee (Percentage-based)

```xml
<ChargeOfferItem InternalCode="late_fee">
    <Name>Late Payment Fee</Name>
    <Description>Charged when rent is paid after the 5th of the month</Description>
    <Characteristics>
        <ChargeRequirement>Conditional</ChargeRequirement>
        <ConditionalInternalCode>rent</ConditionalInternalCode>
        <Lifecycle>During Term</Lifecycle>
        <PaymentFrequency>Per-occurrence</PaymentFrequency>
        <Refundability>Non-refundable</Refundability>
    </Characteristics>
    <AmountBasis>Percentage Of</AmountBasis>
    <PercentageOfCode>rent</PercentageOfCode>
    <ChargeOfferAmount>
        <Amounts></Amounts>
        <Percentage>10.00</Percentage>
    </ChargeOfferAmount>
</ChargeOfferItem>
```

✅ **Valid** (if `rent` item exists): Conditional, percentage-based, references existing code.

### Scenario 3: Pet Deposit

```xml
<PetOfferItem InternalCode="pet_deposit">
    <Name>Pet Deposit</Name>
    <Description>Refundable deposit for pets</Description>
    <Allowed>Yes</Allowed>
    <MaximumWeight>50lb</MaximumWeight>
    <Characteristics>
        <ChargeRequirement>Optional</ChargeRequirement>
        <Lifecycle>Move-in</Lifecycle>
        <PaymentFrequency>One-time</PaymentFrequency>
        <Refundability>Deposit</Refundability>
        <RefundabilityMaxType>Percentage</RefundabilityMaxType>
        <RefundabilityMax>100</RefundabilityMax>
    </Characteristics>
    <AmountBasis>Explicit</AmountBasis>
    <ChargeOfferAmount>
        <Amounts>300.00</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
</PetOfferItem>
```

✅ **Valid**: Pet-specific fields, deposit with refundability details.

### Scenario 4: Included Amenity

```xml
<ChargeOfferItem InternalCode="water">
    <Name>Water</Name>
    <Description>Water service included in rent</Description>
    <Characteristics>
        <ChargeRequirement>Included</ChargeRequirement>
        <Lifecycle>During Term</Lifecycle>
    </Characteristics>
    <AmountBasis></AmountBasis>
    <ChargeOfferAmount>
        <Amounts></Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
</ChargeOfferItem>
```

✅ **Valid**: Included item with empty amounts and basis.

## Understanding Error Messages

Error messages follow this format:

```
[RULE_ID] Description of error at /path/to/element
```

Example:

```
[F.27] Offer item in class 'APP' missing required non-empty 'InternalCode' attribute
```

- **`F.27`**: Rule ID (Section F, Rule 27)
- **Description**: What went wrong
- **Path**: Where in the document (optional)

### Rule ID Prefixes

| Prefix | Section | Topic |
|--------|---------|-------|
| A | Section A | XML basics |
| F | Section F | Item structure |
| G | Section G | Characteristics |
| H | Section H | Amount basis |
| O | Section O | References |
| T | Section T | Duplicates |

## Development

### Run Tests

```bash
# All tests
make test

# MITS validator tests only
pytest tests/validators/mits/ -v

# With coverage
pytest tests/validators/mits/ --cov=app/validators/mits
```

### Add Custom Validation

See [MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md) for detailed instructions on extending the validator.

## API Endpoints

### `POST /v5.0/validate`

Validates MITS 5.0 XML documents.

**Request:**
- **Content-Type**: `application/xml` or `text/xml`
- **Body**: Raw XML document

**Response:**
```json
{
    "valid": boolean,
    "errors": ["array of error messages"],
    "warnings": ["array of warnings"],
    "info": ["array of info messages"]
}
```

**Status Codes:**
- `200 OK`: Validation completed (check `valid` field for result)
- `413 Request Entity Too Large`: Body exceeds 512KB
- `429 Too Many Requests`: Rate limit exceeded

### `GET /healthz`

Health check endpoint.

## Configuration

Environment variables (see `docker-compose.yml`):

```bash
MAX_BODY_BYTES=524288          # 512 KB limit
RATE_LIMIT=60/minute           # Rate limiting
REQUEST_TIMEOUT_SECONDS=2      # Validation timeout
ENABLE_DOCS=true               # OpenAPI docs
```

## Resources

- **Comprehensive Guide**: [MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md)
- **API Docs**: http://localhost:8080/docs (when running)
- **Test Files**: `tests/test_full.xml`, `tests/test_partial.xml`
- **MITS 5.0 Spec**: https://www.naa.org/mits

## Support

For issues or questions:

1. Check error messages for rule IDs
2. Consult [MITS_VALIDATOR_GUIDE.md](MITS_VALIDATOR_GUIDE.md) for rule details
3. Review test files for examples
4. Open an issue with the specific rule ID and XML snippet

---

**Quick validation test**: Send the examples above to verify your installation!

