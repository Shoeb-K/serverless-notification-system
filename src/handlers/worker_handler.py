import json
from src.services.notification_service import process_notification
from src.utils.logger import log_info, log_error

MAX_RETRIES = 3

def lambda_handler(event, context):
    """
    Consumer handler for processing SQS batch events.
    AWS Lambda reads messages from SQS and invokes this function with the batch in 'Records'.
    """
    records = event.get('Records', [])
    log_info(f"Worker up. Received SQS event with {len(records)} records(s).")
    
    for record in records:
        try:
            body = record.get('body')
            message_id = record.get('messageId')
            
            log_info(f"Processing SQS message ID: {message_id}")
            data = json.loads(body)
            
            email = data.get("email", "unknown")
            log_info(f"Processing notification for {email}")
            
            try:
                process_notification(data)
            except Exception as e:
                log_error(f"Failed processing message: {str(e)}")
                raise e  # IMPORTANT → enables SQS retry
            
        except json.JSONDecodeError:
            log_error(f"Failed to parse message body for record: {record.get('messageId')}. Malformed data.")
            # We can log and skip. If we let the exception bubble, it ends up in a DLQ.
            # Usually, bad format messages to a DLQ is desired behavior.
            raise
        except Exception as e:
            # When an exception bubbles up out of the lambda handler, 
            # Lambda fails the entire batch or specific message (depending on configuration),
            # causing the visibility timeout to eventually expire and retry until MaxReceiveCount is hit.
            log_error(f"Unhandled error processing record {record.get('messageId')}: {str(e)}")
            raise

