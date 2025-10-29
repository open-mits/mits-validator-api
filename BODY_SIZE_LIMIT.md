# Request Body Size Limit Configuration

## The Issue

When testing with `test_full.xml` or `test_partial.xml`, you may encounter:

```
app.errors.BodyTooLargeError: 413: Request body too large. 
Maximum allowed size: 524288 bytes
```

## Why This Happens

**File Sizes**:
- `test_full.xml`: **613 KB**
- `test_partial.xml`: **614 KB**

**Default Limit**: **512 KB** (524,288 bytes)

Your XML files are larger than the default security limit!

---

## Solution: Increase MAX_BODY_BYTES

### ✅ Already Fixed!

I've updated the configuration to **1 MB (1,048,576 bytes)** which provides headroom for your files.

**Files Updated**:
1. ✅ `docker-compose.yml` - Line 14: `MAX_BODY_BYTES=1048576`
2. ✅ `.env.example` - `MAX_BODY_BYTES=1048576`

**Container Restarted**: ✅ Changes are now active

---

## Testing Your Files

Now you can test with your large XML files:

```bash
# Test with test_full.xml (613 KB)
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_full.xml

# Test with test_partial.xml (614 KB)  
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_partial.xml
```

---

## Understanding the Limits

### Current Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| **MAX_BODY_BYTES** | 1,048,576 | 1 MB - Maximum request body size |
| **RATE_LIMIT** | 60/minute | Requests per IP address |
| **REQUEST_TIMEOUT_SECONDS** | 2 | Maximum validation time |

### Why Have a Limit?

**Security Protection**:
- ✅ Prevents denial-of-service (DoS) attacks
- ✅ Prevents memory exhaustion
- ✅ Ensures API remains responsive

**Recommended Values**:
- **Development**: 1-5 MB (for testing large files)
- **Production**: 1-2 MB (based on expected file sizes)
- **High-volume**: 500 KB - 1 MB (stricter limits)

---

## Adjusting the Limit

### For Larger Files

If you need to accept files larger than 1 MB:

**Edit `docker-compose.yml`**:
```yaml
environment:
  - MAX_BODY_BYTES=2097152  # 2 MB
  # or
  - MAX_BODY_BYTES=5242880  # 5 MB
```

**Restart**:
```bash
docker-compose down && docker-compose up -d
```

### Common Sizes

| Size | Bytes | Use Case |
|------|-------|----------|
| 512 KB | 524,288 | Small documents |
| **1 MB** | **1,048,576** | **Current (your files)** |
| 2 MB | 2,097,152 | Large documents |
| 5 MB | 5,242,880 | Very large documents |
| 10 MB | 10,485,760 | Maximum recommended |

---

## Environment Variables

You can also use a `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env
MAX_BODY_BYTES=1048576  # 1 MB

# Restart
docker-compose down && docker-compose up -d
```

---

## Checking Current Limit

View the current configuration:

```bash
# Check environment variable
docker exec mits-validator-api env | grep MAX_BODY_BYTES

# Check logs during startup
docker logs mits-validator-api | grep -i "max_body"
```

---

## Production Considerations

### Setting Limits by Environment

**Development** (docker-compose.yml):
```yaml
MAX_BODY_BYTES=5242880  # 5 MB - generous for testing
```

**Production** (environment variables):
```bash
export MAX_BODY_BYTES=1048576  # 1 MB - strict for production
```

### Monitoring

**Watch for**:
- Frequency of 413 errors
- Average file sizes
- Peak file sizes
- Memory usage patterns

**Adjust accordingly**:
- Too many 413s → Increase limit
- High memory usage → Decrease limit
- DoS attempts → Keep limit strict

---

## Testing the Fix

### Quick Test

```bash
# Should now succeed (was failing before)
curl -X POST http://localhost:8080/v5.0/validate \
  -H "Content-Type: application/xml" \
  --data-binary @tests/test_full.xml \
  | jq '.valid, .errors | length, .warnings | length'
```

### Expected Result

```json
{
  "valid": false,
  "errors": [...],  // List of validation errors
  "warnings": [...],
  "info": [...]
}
```

**Status Code**: `200 OK` (not 413 anymore!)

---

## Troubleshooting

### Still Getting 413?

1. **Check container is using new config**:
   ```bash
   docker exec mits-validator-api env | grep MAX_BODY_BYTES
   ```

2. **Restart container**:
   ```bash
   docker-compose restart
   ```

3. **Rebuild if needed**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Checking File Size

```bash
# Check your XML file size
ls -lh tests/test_full.xml
# -rw-rw-rw-  1 user  staff   613K Oct 29 05:10 tests/test_full.xml
```

---

## Summary

✅ **Problem**: XML files (613-614 KB) exceeded 512 KB limit  
✅ **Solution**: Increased `MAX_BODY_BYTES` to 1 MB (1,048,576 bytes)  
✅ **Status**: Applied and container restarted  
✅ **Result**: Your test files should now work!

Now you can successfully validate your large XML files! 🚀

