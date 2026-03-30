import json
import boto3
from src.utils.config import SQS_QUEUE_URL, AWS_REGION
from src.utils.logger import log_info, log_error

# Initialize the SQS client globally for reuse across Lambda invocations
sqs_client = boto3.client('sqs', region_name=AWS_REGION)

def send_to_queue(message: dict) -> bool:
    try:
        log_info(f"Preparing to send message to SQS: {SQS_QUEUE_URL}")
        
        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        
        log_info(f"Successfully sent message to SQS. MessageId: {response.get('MessageId')}")
        return True
        
    except Exception as e:
        log_error(f"Failed to send message to SQS: {str(e)}")
        return False
