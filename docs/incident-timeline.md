# Incident Timeline: NOTIFY-3812

**Incident ID:** NOTIFY-3812  
**Date:** 2024-06-07  
**Duration:** 51 minutes  
**Severity:** P1 - Critical  

---

# Timeline (UTC)

### 08:50 - Deployment Completed

Commit `c82fd19` ("Improve notification retry handling") deployed to production through CI/CD pipeline.

No idempotency validation checks existed for retry replay scenarios.

---

### 09:08 - Detection

CloudWatch alarms triggered:
- Retry queue depth spike
- Elevated SES sending volume
- Increased Lambda retry executions

Customer support also began receiving complaints regarding duplicate emails.

---

### 09:12 - Initial Investigation

On-call engineer observed:
- duplicate welcome emails
- repeated password reset notifications
- retry queue growth

CloudWatch logs showed the same notification IDs being retried multiple times.

---

### 09:16 - Escalation

Incident declared in `#incidents-notifications`

Backend, Platform, and SRE teams joined investigation bridge.

---

### 09:22 - Root Cause Suspected

Engineering identified possible retry replay issue in notification workflow.

Repeated log pattern observed:

```text
notification_id=notif_78291 retry=1
notification_id=notif_78291 retry=2
notification_id=notif_78291 retry=3
```

---

### 09:31 - Root Cause Confirmed

Notification workflow discovered to be non-idempotent in `src/notification_handler.py`

Broken logic:

```python
send_email(user)

raise Exception("temporary failure")
```

The email was successfully delivered before the retry exception was triggered.

This caused:
- duplicate customer emails
- repeated notification processing
- retry queue growth
- elevated SES traffic

Approximately ~14,000 duplicate notifications were delivered during the incident window.

---

### 09:39 - Hotfix Preparation

Branch `hotfix/add-notification-idempotency` created.

Fixes added:
- notification delivery tracking
- idempotency validation
- retry replay protection

---

### 09:47 - Hotfix Validation

Code review completed.

Additional monitoring added for duplicate notification detection.

---

### 09:52 - Hotfix Deployed

Production deployment completed successfully.

Retry workers resumed gradually after deployment verification.

---

### 09:57 - Monitoring Recovery

Retry queue depth returned to expected baseline.

No repeated notification IDs observed in logs.

SES traffic stabilized.

---

### 10:03 - Incident Resolved

All notification processing functioning normally.

Incident status changed to Resolved.

---

### 10:10 - Follow-Up Actions

Action items created for:
- retry replay integration testing
- idempotency validation improvements
- duplicate notification monitoring
- queue retry safeguard checks
