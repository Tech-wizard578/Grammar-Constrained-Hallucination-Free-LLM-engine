# Deployment Checklist: Hallucination-Free LLM Engine

Production deployment guide for the grammar-constrained RAG system.

---

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure all required API keys:
  - [ ] `OPENAI_API_KEY` or `OPENROUTER_API_KEY` or `GROQ_API_KEY`
  - [ ] `TAVILY_API_KEY` (for web search fallback)
- [ ] Review and adjust:
  - [ ] `DEFAULT_MODEL` (e.g., `gpt-4o-mini`)
  - [ ] `SMART_MODEL` (e.g., `gpt-4o`)
  - [ ] `CHUNK_SIZE` (default: 500)
  - [ ] `TOP_K_RETRIEVAL` (default: 5)

### 2. Dependencies

- [ ] Install from lockfile: `pip install -r requirements-lock.txt`
- [ ] Verify Python version: `python --version` (3.9+ required)
- [ ] Test imports: `python -c "import config; import schemas; print('OK')"`

### 3. Knowledge Base

- [ ] Index initial documents:
  ```bash
  python main.py ingest --urls https://your-docs.com
  ```
- [ ] Verify document count:
  ```bash
  python main.py stats
  ```
- [ ] Test query:
  ```bash
  python main.py query "What is your main topic?"
  ```

### 4. Testing

- [ ] Run unit tests: `pytest tests/ -v`
- [ ] Check test coverage: `pytest tests/ --cov=. --cov-report=html`
- [ ] Verify all tests pass (expected: 20 tests)

### 5. Security

- [ ] API keys in secure location (not in git)
- [ ] `.env` file permissions restricted (`chmod 600 .env`)
- [ ] Rate limiting configured (if applicable)
- [ ] HTTPS enabled for any web interfaces

---

## Deployment Options

### Option A: Local/VM Deployment

```bash
# 1. Clone repository
git clone https://github.com/your-repo/hallucination-free-engine.git
cd hallucination-free-engine

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements-lock.txt

# 4. Configure environment
cp .env.template .env
# Edit .env with your API keys

# 5. Run tests
pytest tests/ -v

# 6. Start using
python main.py stats
python main.py query "Your question here"
```

### Option B: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt

COPY . .

ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK CMD python -c "import config" || exit 1

CMD ["python", "main.py", "query", "--help"]
```

```bash
# Build and run
docker build -t hallucination-free-engine .
docker run --env-file .env hallucination-free-engine
```

---

## Post-Deployment Verification

### Smoke Tests

```bash
# 1. Config loads correctly
python -c "from config import get_config_summary; print(get_config_summary())"

# 2. Schemas work
python schemas.py  # Should show "All schema validation tests completed!"

# 3. Query works
python main.py query "What is Python?" 2>&1 | head -50
```

### Monitoring Points

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Query latency | < 5s | > 10s |
| Error rate | < 1% | > 5% |
| Cache hit rate | > 50% | < 20% |
| Hallucination detection rate | < 10% | > 30% |

### Log Locations

- Main logs: `logs/engine.log`
- Error logs: `logs/error.log`
- Rotate policy: 10MB max, 5 backups

---

## Rollback Procedure

1. **Identify issue** via logs: `tail -f logs/error.log`
2. **Rollback code**: `git checkout <previous-commit>`
3. **Restore dependencies**: `pip install -r requirements-lock.txt`
4. **Verify**: `pytest tests/ -v`
5. **Restart service**

---

## Support Contacts

- **Documentation**: See `README.md`
- **Issues**: GitHub Issues
- **Emergency**: Check log files first, then escalate

---

## Version Info

- **Engine Version**: 1.0.0
- **Python**: 3.9+
- **Last Updated**: 2026-01-13
