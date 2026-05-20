def process_notification(notification_id, user):

    send_email(user)

    raise Exception("temporary failure")


def retry_notification(notification_id, user, retry_count):

    if retry_count > 3:
        return "failed"

    return process_notification(notification_id, user)
