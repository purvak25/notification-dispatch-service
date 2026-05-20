# Root Cause Analysis: NOTIFY-3812

**Incident:** Customers receiving duplicate email notifications  
**Date:** 2024-06-07  
**Duration:** 51 minutes (09:08 - 10:03 UTC)  
**Severity:** P1 - Critical  
**Status:** Resolved  

---

# 1. Incident Summary

On June 7, 2024, the `notification-dispatch-service` began sending duplicate email notifications to customers due to a retry handling bug introduced during resiliency improvements.

The issue caused repeated delivery of welcome emails, password reset emails, and billing notifications after temporary processing failures triggered automatic retries.

Approximately 14,000 duplicate notifications were delivered during the incident window before mitigation was completed.

---

# 2. Timeline

| Time (UTC) | Event |
|------------|-------|
| 08:50 | Retry handling deployment completed |
| 09:08 | CloudWatch alarms triggered for retry queue spike |
| 09:16 | Incident escalated to Platform and SRE teams |
| 09:31 | Root cause identified (non-idempotent retry workflow) |
| 09:39 | Hotfix branch created |
| 09:52 | Hotfix deployed to production |
| 09:57 | Retry metrics normalized |
| 10:03 | Incident resolved |

---

# 3. Root Cause

A retry handling refactor introduced a workflow in `src/notification_handler.py` where email delivery occurred before temporary failure handling completed.

Broken implementation:

```python
send_email(user)

raise Exception("temporary failure")
```

The notification was successfully delivered before the retry exception triggered replay processing.

When retries occurred, the same notification ID was processed repeatedly without validation.

### Why it passed local testing

Local testing validated only successful notification delivery scenarios.

Retry replay behavior and temporary downstream failures were not simulated during development testing.

Because the email provider successfully accepted requests, the workflow appeared healthy during local validation.

### Why it bypassed detection

- No idempotency validation existed
- Retry replay scenarios were not covered in automated tests
- Monitoring focused on failure rate instead of duplicate deliveries
- Notification metrics tracked successful sends but not repeated sends
- Code review focused primarily on resiliency improvements

### Why it caused duplicate notifications

The retry workflow reprocessed already completed email sends because notification delivery state was never persisted before failure handling occurred.

This caused:
- duplicate welcome emails
- repeated password reset emails
- billing notification duplication
- retry queue growth
- elevated SES sending volume

---

# 4. Technical Impact

- Approximately 14,000 duplicate notifications delivered
- Retry queue depth increased 5x above baseline
- SES sending volume increased significantly
- Lambda retry executions spiked
- Notification processing latency increased
- Duplicate notification IDs observed repeatedly in logs

### Error Types Observed

- `temporary failure`
- duplicate notification warnings
- retry queue threshold alerts
- elevated Lambda retry executions

---

# 5. Business Impact

- Customers received repeated email notifications
- Support ticket volume increased significantly
- Password reset workflows created customer confusion
- Billing notification duplication caused trust concerns
- Engineering and SRE teams diverted from sprint work
- Notification delivery SLAs temporarily breached

---

# 6. Resolution

- Added notification delivery tracking
- Added idempotency validation
- Added duplicate notification safeguards
- Added retry replay protection
- Added monitoring for repeated notification IDs
- Redeployed hotfix to production

Hotfix deployed within 21 minutes of root cause identification.

---

# 7. Preventive Actions

| Action | Owner | Ticket | Target Date |
|--------|-------|--------|-------------|
| Add retry replay integration tests | Backend | NOTIFY-3813 | 2024-06-11 |
| Add idempotency validation framework | Platform | NOTIFY-3814 | 2024-06-10 |
| Add duplicate notification alerts | SRE | NOTIFY-3815 | 2024-06-09 |
| Add retry workflow monitoring | Platform | NOTIFY-3816 | 2024-06-12 |
| Improve notification audit logging | Backend | NOTIFY-3817 | 2024-06-14 |
| Expand queue resiliency testing | QA | NOTIFY-3818 | 2024-06-15 |

---

# 8. Lessons Learned

- Retry workflows must always be idempotent.
- Notification delivery state should be persisted before retries occur.
- Duplicate delivery monitoring is essential for customer-facing systems.
- Temporary failures can create major downstream customer impact.
- Queue replay scenarios should always be included in testing.
- Monitoring should detect abnormal duplicate processing behavior.

---

# 9. Attachments

- AWS Log Snippet
- Slack Thread
- Jira Ticket
- Incident Timeline
