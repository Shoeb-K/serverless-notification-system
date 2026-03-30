import os

# AWS Configurations
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/NotificationQueue")

# SES Configurations
SES_SENDER_EMAIL = os.environ.get("SES_SENDER_EMAIL", "noreply@example.com")
