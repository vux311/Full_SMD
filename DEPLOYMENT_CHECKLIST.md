# 🚀 DEPLOYMENT CHECKLIST

## Pre-Deployment Verification

### ✅ Code Quality
- [x] All critical fixes applied
- [x] All tests passing (8/8)
- [x] Code reviewed
- [x] No syntax errors
- [ ] No linting errors (run: `flake8 apps/api/src`)

### ✅ Configuration
- [ ] Environment variables set in `.env`
  - [ ] `DATABASE_URI` configured
  - [ ] `SECRET_KEY` set
  - [ ] `GEMINI_API_KEY` configured (for AI features)
  - [ ] `ENVIRONMENT` set to 'production'
  - [ ] `DEBUG` set to False

### ✅ Database
- [ ] Database server accessible
- [ ] Connection string tested
- [ ] Tables created (run migrations)
- [ ] Seed data loaded (if needed)
- [ ] Backup strategy in place

### ✅ Dependencies
```bash
# Install all dependencies
cd apps/api
pip install -r src/requirements.txt
```

### ✅ Manual Smoke Tests

#### Test 1: App Startup
```bash
cd apps/api/src
python app.py

# Expected output:
# ✓ Dependency injection wiring successful
# ✓ Database initialized successfully
# ✓ Middleware registered
# * Running on http://127.0.0.1:5000
```

#### Test 2: Health Check
```bash
# If app is running on port 5000
curl http://localhost:5000/
```

#### Test 3: Authentication
```bash
# Test login endpoint
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}'

# Expected: 200 OK with token (or 401 if credentials invalid)
```

#### Test 4: Protected Endpoint
```bash
# Test that workflow endpoints require auth
curl -X POST http://localhost:5000/syllabuses/1/submit \
  -H "Content-Type: application/json"

# Expected: 401 Unauthorized (missing token)

# With token:
curl -X POST http://localhost:5000/syllabuses/1/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Expected: 200 OK or proper error
```

#### Test 5: Database Connection
```bash
# Test any read endpoint
curl http://localhost:5000/subjects/

# Expected: 200 OK with list of subjects
```

#### Test 6: AI Generation (if configured)
```bash
curl -X POST http://localhost:5000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"subject_name": "Python Programming"}'

# Expected: 200 OK with generated syllabus (or error if API key missing)
```

### ✅ Performance Tests

#### Test 7: Concurrent Requests
```bash
# Install Apache Bench if needed
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Test with 100 concurrent requests
ab -n 100 -c 10 http://localhost:5000/subjects/

# Check:
# - No errors
# - Reasonable response times
# - No connection pool exhaustion
```

#### Test 8: Session Isolation
```python
# Create test script: test_session_isolation.py
import requests
import concurrent.futures

def make_request(n):
    response = requests.get('http://localhost:5000/subjects/')
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(make_request, range(100)))
    
print(f"Success rate: {results.count(200)}/100")
# Expected: 100/100 success
```

### ✅ Security Checks

- [ ] All sensitive endpoints have `@token_required`
- [ ] JWT secret is strong and secure
- [ ] No hardcoded credentials in code
- [ ] Database credentials not in version control
- [ ] CORS configured for production domains only
- [ ] SQL injection protection (using ORM)
- [ ] Input validation on all endpoints

### ✅ Logging & Monitoring

- [ ] App logging configured
- [ ] Error tracking setup (e.g., Sentry)
- [ ] Database query logging (in development only)
- [ ] API request logging
- [ ] Performance metrics collection

### ✅ Documentation

- [x] Code review report completed
- [x] Fix documentation created
- [x] Verification tests documented
- [ ] API documentation updated (Swagger)
- [ ] Deployment guide created
- [ ] Rollback plan documented

---

## Deployment Steps

### Step 1: Backup
```bash
# Backup current production database
pg_dump -h HOST -U USER DATABASE > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Deploy Code
```bash
# Pull latest code
git pull origin main

# Install dependencies
cd apps/api
pip install -r src/requirements.txt
```

### Step 3: Database Migrations
```bash
# Run migrations if any
cd apps/api/src
python -m flask db upgrade  # if using Flask-Migrate

# Or manual migrations
# python migrate_script.py
```

### Step 4: Configuration
```bash
# Verify environment variables
echo $DATABASE_URI
echo $SECRET_KEY
echo $ENVIRONMENT

# Should all be set
```

### Step 5: Start Application
```bash
# Using gunicorn (production WSGI server)
cd apps/api/src
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or using systemd service
sudo systemctl restart syllabus-api
```

### Step 6: Verify Deployment
```bash
# Run verification script
cd apps/api/src
python verify_fixes.py

# Should show: 🎉 ALL TESTS PASSED!
```

### Step 7: Smoke Test Production
```bash
# Test production endpoint
curl https://your-production-domain.com/subjects/

# Expected: 200 OK
```

### Step 8: Monitor
```bash
# Watch logs
tail -f /var/log/syllabus-api/app.log

# Check for:
# - ✓ Dependency injection wiring successful
# - ✓ Database initialized successfully
# - No error messages
```

---

## Post-Deployment

### Immediate (Next 1 hour)
- [ ] Monitor error logs
- [ ] Check response times
- [ ] Verify all endpoints accessible
- [ ] Test critical workflows (login, submit, approve)
- [ ] Check database connections (no pool exhaustion)

### First 24 Hours
- [ ] Monitor error rate
- [ ] Check server resources (CPU, memory, connections)
- [ ] Review user feedback
- [ ] Verify AI features working (if applicable)
- [ ] Check workflow state transitions

### First Week
- [ ] Analyze performance metrics
- [ ] Review any error spikes
- [ ] Gather user feedback
- [ ] Plan optimizations if needed

---

## Rollback Plan

### If Issues Occur

**Step 1: Stop new traffic**
```bash
# Take app offline temporarily
sudo systemctl stop syllabus-api
```

**Step 2: Restore previous version**
```bash
# Checkout previous commit
git checkout <previous-commit-hash>

# Restart app
sudo systemctl start syllabus-api
```

**Step 3: Restore database (if needed)**
```bash
# Only if schema changes were made
psql -h HOST -U USER DATABASE < backup_YYYYMMDD_HHMMSS.sql
```

**Step 4: Verify rollback**
```bash
curl https://your-production-domain.com/subjects/
# Should be working
```

**Step 5: Investigate issue**
- Check logs
- Review error messages
- Test locally
- Fix and redeploy

---

## Emergency Contacts

- **DevOps Lead:** [Name/Contact]
- **Database Admin:** [Name/Contact]
- **Backend Lead:** [Name/Contact]
- **On-call Engineer:** [Name/Contact]

---

## Success Criteria

✅ Deployment is successful if:
- All endpoints respond with correct status codes
- No 500 errors in logs
- Authentication works correctly
- Database connections stable
- Response times < 500ms (p95)
- Error rate < 1%
- Workflow operations complete successfully
- AI generation works (if configured)

---

**Status:** Ready for deployment ✅  
**Last Updated:** January 13, 2026  
**Next Review:** After deployment
