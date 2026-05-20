# NOTIFY-3812

## Summary

Customers receiving duplicate email notifications after retry processing failures.

---

## Severity

P1 - Critical

---

## Symptoms

- Duplicate welcome emails delivered
- Password reset emails received multiple times
- Billing notifications resent repeatedly
- Retry queue depth increased significantly
- SES sending volume spiked unexpectedly

---

## Detection

CloudWatch alerts triggered for:
- elevated retry queue processing
- abnormal SES send rate
- increased Lambda retry executions

Customer support also reported multiple complaints regarding repeated notifications.

---

## Root Cause

Notification delivery workflow was not idempotent.

Emails were sent successfully before temporary failure exceptions triggered retry handling.

The same notification ID was processed repeatedly during retries.

Broken logic:

```python
send_email(user)

raise Exception("temporary failure")
```

---

## Resolution

- Added notification delivery tracking
- Added idempotency validation
- Added duplicate notification protection
- Added retry replay safeguards

---

## Status

Resolved
