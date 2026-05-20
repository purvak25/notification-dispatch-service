# notification-dispatch-service

Production incident simulation repository.

This project simulates a realistic backend production incident where retry handling logic caused duplicate email notifications to be sent to customers after temporary processing failures.

The incident resulted in repeated customer emails, increased retry queue processing, and elevated AWS notification traffic.

---

# Architecture

+----------------------+     +-------------------------------+     +----------------------+
|  Notification Queue  |---->| notification-dispatch-service |---->|  Email Provider      |
|   (SQS/EventBridge)  |     |     (AWS Lambda/Python)       |     |    (AWS SES)         |
+----------------------+     +-------------------------------+     +----------------------+

---

# Components

src/notification_handler.py - Notification processing workflow  
config/env.example - Environment configuration template  
docs/RCA.md - Root cause analysis documentation  
docs/aws-log-snippet.txt - CloudWatch production logs  
docs/slack-thread.md - Incident investigation discussion  
docs/jira-ticket.md - Jira incident summary  
docs/incident-timeline.md - Full production timeline  

---

# Notification Flow

1. Notification event received from queue
2. Email notification generated
3. Delivery request sent to provider
4. Delivery status recorded
5. Metrics and logs emitted to CloudWatch

---

# Incident Simulation

This repository contains the evolution of a realistic production incident involving duplicate notification delivery caused by retry logic failures.

---

# Stage 1 - Initial Implementation

Commit: Implement notification delivery workflow

Notifications processed successfully with retry handling and queue processing support.

---

# Stage 2 - Retry Bug Introduced

Commit: Improve temporary failure retry handling

A retry handling refactor introduced a bug where email delivery occurred before failure state processing completed.

Broken implementation:

```python
send_email(user)

raise Exception("temporary failure")
```

The exception triggered retry processing after the email had already been sent.

This caused:
- duplicate customer emails
- repeated notification retries
- increased SES traffic
- retry queue growth
- inconsistent delivery metrics

---

# Why it passed local testing

Local testing validated only successful delivery scenarios.

Temporary provider failures and retry replay behavior were not simulated during testing.

The email provider accepted requests successfully, so notifications appeared healthy during development validation.

---

# Why it bypassed detection

- No idempotency validation existed
- Retry replay scenarios were not covered in automated tests
- Monitoring focused on failures instead of duplicate deliveries
- Notification metrics tracked success rate but not duplicate sends
- Code review focused primarily on retry resiliency improvements

---

# Stage 3 - Hotfix & Prevention

Commit: Add idempotency validation to notification workflow

Fixes added:
- notification delivery tracking
- idempotency validation
- retry replay protection
- duplicate notification monitoring

---

# Monitoring Metrics

During the incident, these metrics degraded significantly:

| Metric | Normal | Incident |
|--------|--------|----------|
| notification_success_rate | 99% | 96% |
| duplicate_notifications | 0 | ~14,000 |
| retry_queue_depth | baseline | 5x increase |
| SES sending volume | normal | 3x spike |
| customer complaints | low | elevated |

---

# Lessons Learned

- Retry workflows must always be idempotent.
- Email delivery confirmation should happen before retry scheduling.
- Duplicate delivery monitoring is critical in notification systems.
- Temporary failures can create major downstream customer impact.
- Queue replay scenarios should always be included in testing.

---

# Repository Structure

notification-dispatch-service/
├── src/
│   └── notification_handler.py
├── docs/
│   ├── jira-ticket.md
│   ├── slack-thread.md
│   ├── incident-timeline.md
│   ├── RCA.md
│   └── aws-log-snippet.txt
├── config/
│   └── env.example
├── package.json
├── README.md
└── .gitignore

---

# License

MIT - For educational and portfolio use only.
