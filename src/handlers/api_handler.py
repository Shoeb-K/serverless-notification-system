import json
from src.utils.validator import validate_notification_request
from src.services.sqs_service import send_to_queue
from src.utils.logger import log_info, log_error

def lambda_handler(event, context):
    """
    Producer Handler for parsing API Gateway events and pushing valid requests to SQS.
    """
    log_info("Received API request")
    
    try:
        # Extract body from API Gateway event
        body = event.get('body')
        if not body:
            return _build_response(400, {"error": "Missing request body."})
        
        # Parse JSON payload
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body
            
        # Validate data
        is_valid, error_msg = validate_notification_request(data)
        if not is_valid:
            log_error(f"Validation failed: {error_msg}")
            return _build_response(400, {"error": error_msg})
            
        # Deposit into SQS (Decoupling)
        success = send_to_queue(data)
        
        if success:
            log_info("Successfully queued notification request.")
            return _build_response(202, {"message": "Notification accepted for processing."})
        else:
            return _build_response(500, {"error": "Internal server error. Failed to queue message."})
            
    except json.JSONDecodeError:
        log_error("Failed to parse JSON body.")
        return _build_response(400, {"error": "Invalid JSON format."})
    except Exception as e:
        log_error(f"Unexpected error in API handler: {str(e)}")
        return _build_response(500, {"error": "Internal server error."})

def _build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }
