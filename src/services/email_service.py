import boto3
from src.utils.config import SES_SENDER_EMAIL, AWS_REGION
from src.utils.logger import log_info, log_error

# Initialize the SES client globally for reuse
ses_client = boto3.client('ses', region_name=AWS_REGION)

def send_email(to_email: str, message: str) -> bool:
    try:
        log_info(f"Attempting to send email to {to_email}")
        
        response = ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={
                'ToAddresses': [to_email]
            },
            Message={
                'Subject': {
                    'Data': 'New Notification Received'
                },
                'Body': {
                    'Text': {
                        'Data': message
                    }
                }
            }
        )
        
        log_info(f"Successfully sent email to {to_email}. MessageId: {response.get('MessageId')}")
        return True
        
    except Exception as e:
        log_error(f"Failed to send email to {to_email}: {str(e)}")
        return False
