# Slack Thread

**Channel:** #incidents-notifications  
**Date:** 2024-06-07

---

**09:12 AM — Support Engineer**

Multiple customers reporting duplicate email notifications.

Seeing repeated welcome emails and password reset emails.

---

**09:14 AM — SRE Engineer**

CloudWatch shows retry queue depth increasing rapidly.

SES sending volume also spiked after this morning's deployment.

---

**09:16 AM — Backend Engineer**

Checking retry processing changes now.

A retry handling improvement was deployed around 08:50.

---

**09:19 AM — Platform Engineer**

Same notification IDs appearing multiple times in logs.

Example:

```text
notification_id=notif_78291 retry=1
notification_id=notif_78291 retry=2
notification_id=notif_78291 retry=3
```

---

**09:22 AM — Backend Engineer**

Looks like emails are sent before failure handling completes.

Current logic:

```python
send_email(user)

raise Exception("temporary failure")
```

Retries are replaying already completed sends.

---

**09:24 AM — Team Lead**

Can we temporarily disable notification retries?

Need to stop duplicate customer emails immediately.

---

**09:26 AM — Platform Engineer**

Retry workers paused temporarily.

DLQ volume stabilizing now.

---

**09:31 AM — Backend Engineer**

Root cause confirmed.

Notification workflow is not idempotent.

No validation exists to prevent duplicate sends for the same notification ID.

---

**09:35 AM — SRE Engineer**

SES send rate currently 3x above baseline.

Customer complaint tickets increasing quickly.

---

**09:39 AM — Backend Engineer**

Preparing hotfix now.

Adding:
- notification delivery tracking
- idempotency validation
- retry replay protection

---

**09:52 AM — Platform Engineer**

Hotfix deployed successfully.

Retry workers resumed gradually.

---

**09:57 AM — SRE Engineer**

Duplicate notification rate returning to normal.

No repeated notification IDs observed in latest logs.

---

**10:03 AM — Team Lead**

Incident resolved.

Please prepare RCA and postmortem action items before EOD.
