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
            
            _process_with_retries(data, message_id)
            
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

def _process_with_retries(data: dict, message_id: str):
    """
    Simulates a basic runtime retry mechanism for transient processing failures.
    
    DLQ Concept:
    If this function continually fails (e.g., SES goes down entirely),
    the exception raised at the end instructs AWS to return the message to the SQS queue.
    Once the message fails processing more than `MaxReceiveCount` times (configured via AWS), 
    SQS will automatically move the "poison pill" message to a Dead Letter Queue (DLQ).
    This prevents the bad message from clogging the pipeline while ensuring data is securely stored for manual inspection/replay.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            success = process_notification(data)
            if success:
                log_info(f"Successfully processed message {message_id} on attempt {attempt}")
                return
            else:
                log_error(f"Attempt {attempt} failed to process message {message_id} cleanly.")
                
        except Exception as e:
            log_error(f"Exception on attempt {attempt} for message {message_id}: {str(e)}")
            
        if attempt < MAX_RETRIES:
            log_info(f"Retrying message {message_id}... (Attempt {attempt + 1}/{MAX_RETRIES})")
            
    # If we exhaust retries linearly, we raise an error.
    # This explicit failure pushes the responsibility to the SQS -> DLQ infrastructure.
    error_msg = f"All {MAX_RETRIES} processing attempts failed for message {message_id}. Raising error to trigger system retry and potential DLQ routing."
    log_error(error_msg)
    raise Exception(error_msg)
