from src.services.email_service import send_email
from src.utils.logger import log_info, log_error

def process_notification(data: dict) -> bool:
    to_email = data.get("email")
    message = data.get("message")
    
    log_info(f"Processing notification for {to_email}")
    
    # 1. Send Email via SES
    try:
        email_success = send_email(to_email, message)
        if not email_success:
            raise Exception("Initial email dispatch failed")
    except Exception as e:
        log_error("Retrying...")
        email_success = send_email(to_email, message)
    
    # 2. Simulate Push Notification
    # Note: In a production system, this could trigger AWS SNS or a push provider like Firebase.
    if email_success:
        log_info(f"[SIMULATED PUSH NOTIFICATION] Sent to device for user {to_email}: {message[:20]}...")
        return True
    else:
        log_error(f"Aborting push notification due to earlier failures for {to_email}")
        return False
